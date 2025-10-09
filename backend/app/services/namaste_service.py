import pandas as pd
from datetime import datetime
from typing import List, Optional, Dict, Any
from pymongo.database import Database
from app.db.mongodb import get_mongodb
from app.db.redis_client import redis_client
from app.models.schemas import TerminologyCodeResponse, CodeSystemType
import logging

logger = logging.getLogger(__name__)

class NamasteService:
    """Service for NAMASTE terminology processing"""
    
    def __init__(self, db: Database | None = None):
        self.db = db or get_mongodb()
        self.collection = self.db.namaste_codes
    
    async def process_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Process NAMASTE CSV file and store in MongoDB
        
        Expected CSV columns:
        - code: Unique code identifier
        - display: Human-readable term
        - definition: Description
        - ayush_system: ayurveda/siddha/unani
        - category: Classification category
        """
        try:
            # Read CSV
            df = pd.read_csv(file_path)
            
            # Validate required columns
            required_cols = ['code', 'display', 'ayush_system']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            # Process and clean data
            df = df.fillna('')
            codes_processed = 0
            codes_skipped = 0
            
            # Batch insert
            documents = []
            for _, row in df.iterrows():
                # Check if code already exists
                if self.collection.find_one({"code": row['code']}):
                    codes_skipped += 1
                    continue
                
                doc = {
                    "code": row['code'],
                    "display": row['display'],
                    "system": CodeSystemType.NAMASTE.value,
                    "definition": row.get('definition', ''),
                    "ayush_system": row.get('ayush_system', '').lower(),
                    "category": row.get('category', ''),
                    "properties": {},
                    "is_active": True
                }
                documents.append(doc)
                codes_processed += 1
            
            if documents:
                self.collection.insert_many(documents)
            
            # Clear cache
            redis_client.delete("namaste:all_codes")
            
            logger.info(f"Processed {codes_processed} NAMASTE codes, skipped {codes_skipped}")
            
            return {
                "success": True,
                "codes_processed": codes_processed,
                "codes_skipped": codes_skipped,
                "total_codes": self.collection.count_documents({})
            }
            
        except Exception as e:
            logger.error(f"Error processing NAMASTE CSV: {str(e)}")
            raise
    
    async def search_codes(
        self, 
        query: str, 
        ayush_system: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Search NAMASTE codes with text matching"""
        
        # Build search query
        search_filter = {
            "$or": [
                {"display": {"$regex": query, "$options": "i"}},
                {"code": {"$regex": query, "$options": "i"}},
                {"definition": {"$regex": query, "$options": "i"}}
            ]
        }
        
        if ayush_system:
            search_filter["ayush_system"] = ayush_system.lower()
        
        # Execute search
        results = list(
            self.collection
            .find(search_filter)
            .skip(offset)
            .limit(limit)
        )
        
        # Remove MongoDB _id field
        for result in results:
            result.pop('_id', None)
        
        return results
    
    async def get_code_by_id(self, code: str) -> Optional[Dict[str, Any]]:
        """Get specific NAMASTE code"""
        
        # Try cache first
        cache_key = f"namaste:code:{code}"
        cached = redis_client.get(cache_key)
        if cached:
            return cached
        
        # Query database
        result = self.collection.find_one({"code": code})
        if result:
            result.pop('_id', None)
            redis_client.set(cache_key, result)
            return result
        
        return None
    
    def generate_fhir_codesystem(self) -> Dict[str, Any]:
        """Generate FHIR R4 CodeSystem resource"""
        
        codes = list(self.collection.find({}))
        
        return {
            "resourceType": "CodeSystem",
            "id": "namaste-codes",
            "url": "https://namaste.ayush.gov.in/CodeSystem/disorders",
            "version": "1.0.0",
            "name": "NAMASTECodes",
            "title": "NAMASTE - National AYUSH Morbidity & Standardized Terminologies",
            "status": "active",
            "experimental": False,
            "date": datetime.utcnow().isoformat(),
            "publisher": "Ministry of AYUSH, Government of India",
            "description": "Standardized terminology for Ayurveda, Siddha, and Unani disorders",
            "caseSensitive": True,
            "content": "complete",
            "count": len(codes),
            "concept": [
                {
                    "code": code["code"],
                    "display": code["display"],
                    "definition": code.get("definition"),
                    "property": [
                        {
                            "code": "ayush-system",
                            "valueString": code.get("ayush_system")
                        }
                    ] if code.get("ayush_system") else []
                }
                for code in codes
            ]
        }

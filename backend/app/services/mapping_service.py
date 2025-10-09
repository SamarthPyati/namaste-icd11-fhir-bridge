from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sqlalchemy.orm import Session
from app.models.database import ConceptMapping
from app.models.schemas import EquivalenceType, ConceptMappingResponse
from app.db.mongodb import get_mongodb
import logging

logger = logging.getLogger(__name__)

class MappingService:
    """Service for intelligent code mapping"""
    
    def __init__(self):
        self.db = get_mongodb()
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000
        )
    
    async def generate_mappings(
        self,
        source_system: str,
        target_system: str,
        threshold: float = 0.3,
        db: Session | None = None
    ) -> List[Dict[str, Any]]:
        """Generate intelligent mappings between code systems"""
        
        try:
            # Fetch source codes
            source_collection = self.db[f"{source_system}_codes"]
            source_codes = list(source_collection.find({}))
            
            # Fetch target codes
            target_collection = self.db[f"{target_system}_codes"]
            target_codes = list(target_collection.find({}))
            
            if not source_codes or not target_codes:
                logger.warning(f"No codes found for mapping: {source_system} -> {target_system}")
                return []
            
            # Prepare text data for similarity calculation
            source_texts = [
                f"{code.get('display', '')} {code.get('definition', '')}" 
                for code in source_codes
            ]
            target_texts = [
                f"{code.get('display', '')} {code.get('definition', '')}" 
                for code in target_codes
            ]
            
            # Vectorize and calculate similarity
            all_texts = source_texts + target_texts
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            source_matrix = tfidf_matrix[:len(source_texts)]
            target_matrix = tfidf_matrix[len(source_texts):]
            
            similarity_matrix = cosine_similarity(source_matrix, target_matrix)
            
            # Generate mappings
            mappings = []
            for i, source_code in enumerate(source_codes):
                similarities = similarity_matrix[i]
                
                # Find matches above threshold
                best_matches_idx = np.where(similarities >= threshold)[0]
                
                for j in best_matches_idx:
                    target_code = target_codes[j]
                    confidence = float(similarities[j])
                    
                    mapping = {
                        "source_code": source_code["code"],
                        "source_system": source_system,
                        "target_code": target_code["code"],
                        "target_system": target_system,
                        "equivalence": self._determine_equivalence(confidence),
                        "confidence_score": confidence,
                        "is_validated": False
                    }
                    
                    mappings.append(mapping)
                    
                    # Store in database if session provided
                    if db:
                        db_mapping = ConceptMapping(**mapping)
                        db.add(db_mapping)
            
            if db:
                db.commit()
            
            logger.info(f"Generated {len(mappings)} mappings: {source_system} -> {target_system}")
            return mappings
            
        except Exception as e:
            logger.error(f"Error generating mappings: {str(e)}")
            if db:
                db.rollback()
            raise
    
    def _determine_equivalence(self, confidence: float) -> str:
        """Determine equivalence type based on confidence score"""
        if confidence >= 0.9:
            return EquivalenceType.EXACT.value
        elif confidence >= 0.7:
            return EquivalenceType.EQUIVALENT.value
        elif confidence >= 0.5:
            return EquivalenceType.WIDER.value
        else:
            return EquivalenceType.INEXACT.value
    
    async def translate_code(
        self,
        code: str,
        source_system: str,
        target_system: str,
        db: Session
    ) -> List[ConceptMappingResponse]:
        """Translate a code from source to target system"""
        
        # Query existing mappings
        mappings = db.query(ConceptMapping).filter(
            ConceptMapping.source_code == code,
            ConceptMapping.source_system == source_system,
            ConceptMapping.target_system == target_system
        ).order_by(ConceptMapping.confidence_score.desc()).all()
        
        return mappings

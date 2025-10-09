import httpx
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.db.mongodb import get_mongodb
from app.db.redis_client import redis_client
from app.models.schemas import CodeSystemType
import logging

logger = logging.getLogger(__name__)

class ICD11Service:
    """Service for WHO ICD-11 API integration"""
    
    def __init__(self):
        self.base_url = settings.icd11_api_base_url
        self.auth_url = "https://icdaccessmanagement.who.int/connect/token"
        self.client_id = settings.icd11_client_id
        self.client_secret = settings.icd11_client_secret
        self.db = get_mongodb()
        self.collection = self.db.icd11_codes
    
    async def authenticate(self) -> str:
        """Authenticate with ICD-11 API and cache token"""
        
        # Check cache first
        cache_key = "icd11:access_token"
        cached_token = redis_client.get(cache_key)
        if cached_token:
            return cached_token
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.auth_url,
                    data={
                        "grant_type": "client_credentials",
                        "scope": "icdapi_access"
                    },
                    auth=(self.client_id, self.client_secret),
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code != 200:
                    raise Exception(f"ICD-11 authentication failed: {response.text}")
                
                token_data = response.json()
                token = token_data["access_token"]
                
                # Cache for 50 minutes (tokens typically expire in 1 hour)
                redis_client.set(cache_key, token, expiry=3000)
                
                logger.info("✅ Successfully authenticated with ICD-11 API")
                return token
                
        except Exception as e:
            logger.error(f"❌ ICD-11 authentication error: {str(e)}")
            raise
    
    async def fetch_tm2_codes(self) -> Dict[str, Any]:
        """Fetch Traditional Medicine Module 2 codes"""
        
        token = await self.authenticate()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json",
                    "API-Version": "v2",
                    "Accept-Language": "en"
                }
                
                # Fetch TM2 chapter (Chapter 26)
                response = await client.get(
                    f"{self.base_url}/mms/26",
                    headers=headers
                )
                
                if response.status_code != 200:
                    raise Exception(f"Failed to fetch TM2 codes: {response.text}")
                
                data = response.json()
                codes = await self._process_tm2_hierarchy(data, headers, client)
                
                # Store in MongoDB
                if codes:
                    # Clear existing TM2 codes
                    self.collection.delete_many({"system": CodeSystemType.ICD11_TM2.value})
                    self.collection.insert_many(codes)
                
                logger.info(f"✅ Fetched and stored {len(codes)} ICD-11 TM2 codes")
                
                return {
                    "success": True,
                    "codes_fetched": len(codes),
                    "system": CodeSystemType.ICD11_TM2.value
                }
                
        except Exception as e:
            logger.error(f"❌ Error fetching TM2 codes: {str(e)}")
            raise
    
    async def _process_tm2_hierarchy(
        self, 
        data: Dict[str, Any], 
        headers: Dict[str, str],
        client: httpx.AsyncClient
    ) -> List[Dict[str, Any]]:
        """Process TM2 hierarchy recursively"""
        
        codes = []
        
        # Extract main entity data
        if "child" in data:
            for child_url in data["child"]:
                try:
                    # Fetch child entity
                    child_response = await client.get(child_url, headers=headers)
                    if child_response.status_code == 200:
                        child_data = child_response.json()
                        
                        code_entry = {
                            "code": child_data.get("code", ""),
                            "display": self._extract_title(child_data.get("title")),
                            "system": CodeSystemType.ICD11_TM2.value,
                            "definition": self._extract_title(child_data.get("definition")),
                            "uri": child_data.get("@id", ""),
                            "is_active": True
                        }
                        
                        codes.append(code_entry)
                        
                except Exception as e:
                    logger.warning(f"Failed to fetch child entity: {str(e)}")
                    continue
        
        return codes
    
    def _extract_title(self, title_obj: Any) -> str:
        """Extract title from ICD-11 response object"""
        if isinstance(title_obj, dict):
            return title_obj.get("@value", "") or title_obj.get("en", "")
        return str(title_obj) if title_obj else ""
    
    async def search_codes(
        self, 
        query: str, 
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Search ICD-11 codes"""
        
        search_filter = {
            "system": CodeSystemType.ICD11_TM2.value,
            "$or": [
                {"display": {"$regex": query, "$options": "i"}},
                {"code": {"$regex": query, "$options": "i"}},
                {"definition": {"$regex": query, "$options": "i"}}
            ]
        }
        
        results = list(
            self.collection
            .find(search_filter)
            .skip(offset)
            .limit(limit)
        )
        
        for result in results:
            result.pop('_id', None)
        
        return results
import redis
import json
from typing import Any, Optional

from app.core.config import settings

class RedisClient:
    def __init__(self):
        self.client = redis.from_url(
            settings.redis_url,
            decode_responses=True
        )
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        value = self.client.get(key)
        if value:
            return json.loads(value)
        return None
    
    def set(self, key: str, value: Any, expiry: int = None) -> bool:
        """Set value in cache"""
        expiry = expiry or settings.redis_cache_expiry
        return self.client.setex(
            key, 
            expiry, 
            json.dumps(value)
        )
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        return self.client.delete(key)
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return self.client.exists(key)

redis_client = RedisClient()
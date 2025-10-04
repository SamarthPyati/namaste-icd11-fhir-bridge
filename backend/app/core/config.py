from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class AppSettings(BaseSettings):
    """Main Application Settings"""
    
    # Application
    app_name: str = "AYUR-SANKET"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Database
    database_url: str
    mongodb_url: str
    mongodb_db_name: str = "ayur_sanket"
    
    # Redis
    redis_url: str
    redis_cache_expiry: int = 3600  # 1 hour
    
    # ICD-11 API
    icd11_client_id: str
    icd11_client_secret: str
    icd11_api_base_url: str = "https://id.who.int/icd/release/11/2023-01"
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # ABHA (Future implementation)
    abha_client_id: Optional[str] = None
    abha_client_secret: Optional[str] = None
    
    # API Rate Limiting
    rate_limit_per_minute: int = 100
    
    # Background Tasks
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> AppSettings:
    """Get cached settings instance"""
    return AppSettings()

settings = get_settings()

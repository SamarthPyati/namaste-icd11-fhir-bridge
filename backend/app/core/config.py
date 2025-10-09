from pathlib import Path
from functools import lru_cache
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


# TODO: Make a BaseConfig class and distribute across all the environments like prod, test and dev
class AppConfig(BaseSettings):
    """Main app configuration and settings"""
    app_name: str = "AYUR-SANKET"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # Database
    database_url: Optional[str] = Field(None)
    mongodb_url: Optional[str] = Field(None)
    mongodb_db_name: str = "ayur_sanket"

    # Redis
    redis_url: Optional[str] = Field(None)
    redis_cache_expiry: int = 3600

    # ICD-11 API
    icd11_client_id: Optional[str] = Field(None)
    icd11_client_secret: Optional[str] = Field(None)
    icd11_api_base_url: Optional[str] = Field(None)

    # Security
    secret_key: Optional[str] = Field(None)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Rate Limiting
    rate_limit_per_minute: int = 100

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    class Config:
        # .env file located behind two parent directories
        env_file: str = str(Path(__file__).resolve().parents[2] / ".env")
        case_sensitive = False
        extra = "ignore"


@lru_cache
def get_app_config() -> AppConfig: 
    return AppConfig() # type: ignore

settings: AppConfig = get_app_config()
from pydantic import BaseSettings, PostgresDsn, validator
from typing import Optional, Dict, Any, Union, List
import os
from pathlib import Path

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Sepsis Prediction System"
    
    # SECURITY
    SECRET_KEY: str = os.getenv("SECRET_KEY", "highly-secure-secret-key-for-jwt-generation-replace-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # DATABASE
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "sepsis_prediction")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    DATABASE_URI: Optional[PostgresDsn] = None

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    # FHIR API
    FHIR_API_URL: str = os.getenv("FHIR_API_URL", "https://hapi.fhir.org/baseR4")
    FHIR_CLIENT_ID: Optional[str] = os.getenv("FHIR_CLIENT_ID")
    FHIR_CLIENT_SECRET: Optional[str] = os.getenv("FHIR_CLIENT_SECRET")
    
    # ML MODEL
    MODEL_PATH: str = os.getenv(
        "MODEL_PATH", 
        str(Path(__file__).parent.parent.parent / "models" / "sepsis_model.pkl")
    )
    EXPLAINER_PATH: str = os.getenv(
        "EXPLAINER_PATH", 
        str(Path(__file__).parent.parent.parent / "models" / "explainer.pkl")
    )
    FEATURE_CONFIG_PATH: str = os.getenv(
        "FEATURE_CONFIG_PATH", 
        str(Path(__file__).parent.parent.parent / "models" / "feature_config.json")
    )
    
    # NOTIFICATIONS
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    
    # LOGGING
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Omi Configuration
    omi_app_id: str
    omi_app_secret: str
    omi_api_base_url: str = "https://api.omi.me"
    
    # Firebase Configuration
    firebase_credentials_path: str = "./firebase-credentials.json"
    firebase_database_url: str
    
    # OpenAI Configuration
    openai_api_key: str
    
    # Application Configuration
    environment: str = "development"
    log_level: str = "INFO"
    feedback_cooldown_seconds: int = 300
    min_meal_duration_seconds: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
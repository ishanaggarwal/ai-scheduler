import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "AI Scheduler"
    APP_BASE_URL: str = "http://localhost:3000"  # Frontend URL for redirects
    API_BASE_URL: str = "http://localhost:8000"  # Backend URL
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/callback"
    
    # Security
    APP_ENCRYPTION_KEY: str  # 32 url-safe base64-encoded bytes
    
    # Database
    DATABASE_URL: str = "sqlite:///./scheduler.db"
    
    # Feature Flags
    ENABLE_GMAIL_REMINDERS: bool = False

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

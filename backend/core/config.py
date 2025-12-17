"""
Configuration management using pydantic-settings
Loads environment variables and provides type-safe config
"""

from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_TITLE: str = "AI Trading Copilot API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Backend API for conversational trading assistant"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default
        "http://localhost:5174",  # Vite alternative
    ]
    
    # API Keys (loaded from .env)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ALPACA_API_KEY: str = os.getenv("ALPACA_API_KEY", "")
    ALPACA_SECRET_KEY: str = os.getenv("ALPACA_SECRET_KEY", "")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    
    # Trading Configuration
    PAPER_TRADING: bool = True  # Always use paper trading for safety
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True  # Auto-reload on code changes (dev only)
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()
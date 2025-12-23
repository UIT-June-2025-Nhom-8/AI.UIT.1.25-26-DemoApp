"""
Configuration settings for the backend API
"""
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    APP_NAME: str = "Vietnam Housing Price Prediction API"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # CORS Settings
    ALLOWED_ORIGINS: str = "*"  # Can be comma-separated list or "*" for all

    # Authentication Settings (hardcoded for demo)
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Hardcoded accounts for demo
    DEMO_ACCOUNTS: dict = {
        "admin": "admin123",
        "demo": "demo123",
        "user": "user123"
    }

    # Model Settings
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    MODELS_DIR: Path = BASE_DIR / "models"

    # Model files - matching your saved models (updated timestamps)
    MODEL_FILES: dict = {
        "lightgbm": "lightgbm_regressor_20251220_175243.pkl",
        "xgboost": "xgboost_regressor_20251220_175243.pkl",
    }

    # Preprocessing artifacts
    ENCODERS_FILE: str = "encoders_optimized.pkl"
    LOCATION_STATS_FILE: str = "location_stats_optimized.pkl"

    # Default model for prediction
    DEFAULT_MODEL: str = "lightgbm"

    # LLM Parser Settings
    HUGGINGFACE_TOKEN: str = os.getenv("HUGGINGFACE_TOKEN", "")

    # Feature names (should match training data)
    REQUIRED_FEATURES: List[str] = [
        "Area", "Bedrooms", "Bathrooms", "Floors",
        "Frontage", "AccessRoad", "LegalStatus", "Furniture"
    ]

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()

"""
Request schemas for API endpoints
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Login request"""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

    class Config:
        schema_extra = {
            "example": {
                "username": "demo",
                "password": "demo123"
            }
        }


class ParseTextRequest(BaseModel):
    """Parse real estate description text"""
    text: str = Field(..., description="Real estate description in Vietnamese")
    verbose: bool = Field(False, description="Verbose output")

    class Config:
        schema_extra = {
            "example": {
                "text": "Nhà 120m2, 3 phòng ngủ, 2 toilet, quận 7, sổ hồng, hướng đông nam",
                "verbose": False
            }
        }


class PredictRequest(BaseModel):
    """Prediction request with features"""
    features: Dict[str, Any] = Field(..., description="House features")
    model_name: Optional[str] = Field(None, description="Model to use (default: lightgbm)")
    use_ensemble: bool = Field(False, description="Use all models and return ensemble prediction")

    class Config:
        schema_extra = {
            "example": {
                "features": {
                    "Area": 120,
                    "Bedrooms": 3,
                    "Bathrooms": 2,
                    "Floors": 2,
                    "Frontage": 5,
                    "AccessRoad": 4,
                    "District": "Quận 7",
                    "LegalStatus": "Sổ hồng",
                    "Furniture": "Đầy đủ"
                },
                "model_name": "lightgbm",
                "use_ensemble": False
            }
        }


class ParseAndPredictRequest(BaseModel):
    """Parse text and predict in one request"""
    text: str = Field(..., description="Real estate description in Vietnamese")
    model_name: Optional[str] = Field(None, description="Model to use")
    use_ensemble: bool = Field(False, description="Use ensemble prediction")

    class Config:
        schema_extra = {
            "example": {
                "text": "Nhà 120m2, 3PN, 2WC, quận 7, sổ hồng",
                "model_name": "lightgbm",
                "use_ensemble": False
            }
        }

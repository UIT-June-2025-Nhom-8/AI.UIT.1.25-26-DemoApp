"""
Response schemas for API endpoints
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class LoginResponse(BaseModel):
    """Login response with access token"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    username: str = Field(..., description="Username")


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str = Field(..., description="Message")


class ParseResponse(BaseModel):
    """Parse response with extracted features"""
    success: bool = Field(..., description="Whether parsing was successful")
    features: Dict[str, Any] = Field({}, description="Extracted features")
    raw_text: str = Field(..., description="Original input text")


class PredictionResponse(BaseModel):
    """Single model prediction response"""
    prediction: float = Field(..., description="Predicted house price (VND)")
    prediction_formatted: str = Field(..., description="Formatted prediction (e.g., '5.2 tỷ')")
    confidence: float = Field(..., description="Confidence score (0-100)")
    model_used: str = Field(..., description="Model name used for prediction")
    features_used: Dict[str, Any] = Field(..., description="Features used for prediction")


class EnsemblePredictionResponse(BaseModel):
    """Ensemble prediction response from multiple models"""
    ensemble_prediction: float = Field(..., description="Ensemble predicted price (VND)")
    ensemble_prediction_formatted: str = Field(..., description="Formatted ensemble prediction")
    ensemble_std: float = Field(..., description="Standard deviation of predictions")
    confidence: float = Field(..., description="Ensemble confidence score (0-100)")
    individual_predictions: Dict[str, Any] = Field(..., description="Predictions from each model")
    models_used: List[str] = Field(..., description="List of models used")
    features_used: Dict[str, Any] = Field(..., description="Features used for prediction")


class ModelInfoResponse(BaseModel):
    """Model information response"""
    name: str = Field(..., description="Model name")
    available: bool = Field(..., description="Whether model is available")
    metadata: Dict[str, Any] = Field({}, description="Model metadata")


class AvailableModelsResponse(BaseModel):
    """Available models list response"""
    models: List[str] = Field(..., description="List of available model names")
    default_model: str = Field(..., description="Default model name")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    models_loaded: int = Field(..., description="Number of models loaded")
    llm_available: bool = Field(..., description="Whether LLM parsing is available")

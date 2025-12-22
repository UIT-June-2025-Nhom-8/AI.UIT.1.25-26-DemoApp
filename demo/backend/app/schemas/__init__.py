"""
Schemas module for backend API
"""
from .request import (
    LoginRequest,
    ParseTextRequest,
    PredictRequest,
    ParseAndPredictRequest
)
from .response import (
    LoginResponse,
    MessageResponse,
    ParseResponse,
    PredictionResponse,
    EnsemblePredictionResponse,
    ModelInfoResponse,
    AvailableModelsResponse,
    HealthResponse
)

__all__ = [
    # Request schemas
    "LoginRequest",
    "ParseTextRequest",
    "PredictRequest",
    "ParseAndPredictRequest",
    # Response schemas
    "LoginResponse",
    "MessageResponse",
    "ParseResponse",
    "PredictionResponse",
    "EnsemblePredictionResponse",
    "ModelInfoResponse",
    "AvailableModelsResponse",
    "HealthResponse"
]

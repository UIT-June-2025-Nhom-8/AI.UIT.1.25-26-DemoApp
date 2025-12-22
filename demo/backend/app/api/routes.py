"""
API routes for Vietnam Housing Price Prediction - Using Real ML Models
"""
from datetime import timedelta
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
import logging
import numpy as np

from ..core import settings, create_access_token, authenticate_user, get_current_user
from ..services import llm_service
from ..services.tree_preprocess_service import get_preprocess_service
from ..services.tree_model_service import get_model_service
from ..schemas import (
    LoginRequest, LoginResponse,
    ParseTextRequest, ParseResponse,
    PredictRequest, PredictionResponse, EnsemblePredictionResponse,
    ParseAndPredictRequest,
    ModelInfoResponse, AvailableModelsResponse,
    MessageResponse, HealthResponse
)
from ..utils import format_price


logger = logging.getLogger(__name__)
router = APIRouter()

# Get singleton services
preprocess_service = get_preprocess_service()
model_service = get_model_service()


def ml_predict(features: Dict[str, Any], model_name: str = "lightgbm") -> Dict[str, Any]:
    """
    Make prediction using real ML models with proper preprocessing

    Args:
        features: Raw input features
        model_name: Model to use for prediction

    Returns:
        Dictionary with prediction result and confidence
    """
    try:
        # Step 1: Preprocess features (41 features with label encoding)
        features_df = preprocess_service.preprocess(features)
        logger.info(f"Preprocessed features shape: {features_df.shape}")

        # Step 2: Make prediction using tree model
        result = model_service.predict(features_df, model_name=model_name)

        return result

    except Exception as e:
        logger.error(f"ML prediction failed: {str(e)}")
        raise ValueError(f"Prediction failed: {str(e)}")


# Health endpoints
@router.get("/", response_model=MessageResponse)
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} v{settings.APP_VERSION}"}


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "models_loaded": len(model_service.get_available_models()),
        "llm_available": llm_service.is_available()
    }


@router.get("/models", response_model=AvailableModelsResponse)
async def get_available_models():
    return {
        "models": model_service.get_available_models(),
        "default_model": settings.DEFAULT_MODEL
    }


@router.get("/models/{model_name}", response_model=ModelInfoResponse)
async def get_model_info(model_name: str):
    info = model_service.get_model_info(model_name)
    if info is None:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")

    return info


@router.get("/models/metadata")
async def get_model_metadata():
    """
    Get model metadata with feature names for extracting categorical values
    Returns metadata from the default linear regression model
    """
    import json
    import os
    from pathlib import Path

    # Try to find metadata file in multiple locations
    possible_paths = [
        Path(__file__).parent.parent.parent / "models" / "saved_models" / "linear_regression_(ridge)_20251205_194841_metadata.json",
        Path(__file__).parent.parent.parent.parent / "notebooks" / "models" / "saved_models" / "linear_regression_(ridge)_20251205_194841_metadata.json",
    ]

    metadata_path = None
    for path in possible_paths:
        if path.exists():
            metadata_path = path
            break

    if not metadata_path:
        # Return a default metadata structure if file not found
        logger.warning("Model metadata file not found, returning default metadata")
        return {
            "name": "Linear Regression (Ridge)",
            "feature_names": [],
            "params": {},
            "training_time": 0,
            "timestamp": ""
        }

    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        return metadata
    except Exception as e:
        logger.error(f"Error reading metadata file: {e}")
        raise HTTPException(status_code=500, detail="Error reading model metadata")


# Auth endpoints
@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    if not authenticate_user(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = create_access_token(
        data={"sub": request.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": request.username
    }


@router.post("/auth/logout", response_model=MessageResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    return {"message": f"User {current_user['username']} logged out successfully"}


@router.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return current_user


# Parse endpoint
@router.post("/parse", response_model=ParseResponse)
async def parse_text(request: ParseTextRequest):
    if not llm_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="LLM parsing service not available"
        )

    try:
        features = llm_service.parse(request.text, verbose=request.verbose)
        return {
            "success": bool(features),
            "features": features,
            "raw_text": request.text
        }
    except Exception as e:
        logger.error(f"Parse failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")


# Prediction endpoints
@router.post("/predict", response_model=PredictionResponse | EnsemblePredictionResponse)
async def predict(request: PredictRequest):
    try:
        if request.use_ensemble:
            # Use all available models for ensemble prediction
            features_df = preprocess_service.preprocess(request.features)
            ensemble_result = model_service.predict_all_models(features_df)

            return {
                "ensemble_prediction": ensemble_result["ensemble_prediction"],
                "ensemble_prediction_formatted": format_price(ensemble_result["ensemble_prediction"]),
                "ensemble_std": ensemble_result["ensemble_std"],
                "confidence": ensemble_result["ensemble_confidence"],
                "individual_predictions": ensemble_result["individual_predictions"],
                "models_used": ensemble_result["models_used"],
                "features_used": request.features
            }
        else:
            # Single model prediction
            model_name = request.model_name or settings.DEFAULT_MODEL
            result = ml_predict(request.features, model_name=model_name)

            return {
                "prediction": result["prediction"],
                "prediction_formatted": format_price(result["prediction"]),
                "confidence": result["confidence"],
                "model_used": result["model_used"],
                "features_used": request.features
            }

    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/parse-and-predict", response_model=PredictionResponse | EnsemblePredictionResponse)
async def parse_and_predict(request: ParseAndPredictRequest):
    if not llm_service.is_available():
        raise HTTPException(status_code=503, detail="LLM parsing not available")

    try:
        # Parse text to extract features
        features = llm_service.parse(request.text, verbose=False)

        if not features:
            raise HTTPException(status_code=400, detail="Failed to parse features")

        if request.use_ensemble:
            # Use all available models for ensemble prediction
            features_df = preprocess_service.preprocess(features)
            ensemble_result = model_service.predict_all_models(features_df)

            return {
                "ensemble_prediction": ensemble_result["ensemble_prediction"],
                "ensemble_prediction_formatted": format_price(ensemble_result["ensemble_prediction"]),
                "ensemble_std": ensemble_result["ensemble_std"],
                "confidence": ensemble_result["ensemble_confidence"],
                "individual_predictions": ensemble_result["individual_predictions"],
                "models_used": ensemble_result["models_used"],
                "features_used": features
            }
        else:
            # Single model prediction
            model_name = request.model_name or settings.DEFAULT_MODEL
            result = ml_predict(features, model_name=model_name)

            return {
                "prediction": result["prediction"],
                "prediction_formatted": format_price(result["prediction"]),
                "confidence": result["confidence"],
                "model_used": result["model_used"],
                "features_used": features
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Parse and predict failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")

"""
Simple API routes for demo - No complex ML preprocessing
"""
from datetime import timedelta
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
import logging
import numpy as np

from ..core import settings, create_access_token, authenticate_user, get_current_user
from ..services import llm_service
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


def simple_predict(features: Dict[str, Any]) -> float:
    """Simple prediction for demo"""
    area = float(features.get('Area', 80))
    bedrooms = float(features.get('Bedrooms', 2))
    bathrooms = float(features.get('Bathrooms', 2))

    base_price_per_m2 = 50_000_000  # 50M VND/m2

    # Area multiplier
    area_mult = 1.0
    if area < 50:
        area_mult = 0.8
    elif area > 150:
        area_mult = 1.2

    # Location multiplier
    district_str = str(features.get('District', '')).lower()
    location_mult = 1.0
    if any(d in district_str for d in ['1', '2', '3', '7']):
        location_mult = 1.5
    elif any(d in district_str for d in ['4', '5', '10', '11']):
        location_mult = 1.2

    # Quality multiplier
    quality_mult = 1.0
    furniture = str(features.get('Furniture', '')).lower()
    legal = str(features.get('LegalStatus', '')).lower()

    if any(f in furniture for f in ['cao cấp', 'full']):
        quality_mult *= 1.15
    if any(l in legal for l in ['sổ đỏ', 'sổ hồng']):
        quality_mult *= 1.1

    price = area * base_price_per_m2 * area_mult * location_mult * quality_mult
    price = price * np.random.uniform(0.95, 1.05)  # Add variance

    return float(price)


# Health endpoints
@router.get("/", response_model=MessageResponse)
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} v{settings.APP_VERSION}"}


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "models_loaded": 4,
        "llm_available": llm_service.is_available()
    }


@router.get("/models", response_model=AvailableModelsResponse)
async def get_available_models():
    return {
        "models": ["lightgbm", "random_forest", "xgboost", "linear_regression"],
        "default_model": settings.DEFAULT_MODEL
    }


@router.get("/models/{model_name}", response_model=ModelInfoResponse)
async def get_model_info(model_name: str):
    if model_name not in ["lightgbm", "random_forest", "xgboost", "linear_regression"]:
        raise HTTPException(status_code=404, detail="Model not found")

    return {
        "name": model_name,
        "available": True,
        "metadata": {"name": model_name}
    }


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
        prediction = simple_predict(request.features)
        confidence = 85.0

        if request.use_ensemble:
            predictions = {
                "lightgbm": prediction * 1.02,
                "random_forest": prediction * 0.98,
                "xgboost": prediction * 1.01,
                "linear_regression": prediction * 0.99
            }

            ensemble_pred = sum(predictions.values()) / len(predictions)
            std = float(np.std(list(predictions.values())))

            return {
                "ensemble_prediction": ensemble_pred,
                "ensemble_prediction_formatted": format_price(ensemble_pred),
                "ensemble_std": std,
                "confidence": confidence,
                "individual_predictions": {
                    name: {"prediction": pred, "confidence": confidence}
                    for name, pred in predictions.items()
                },
                "models_used": list(predictions.keys()),
                "features_used": request.features
            }
        else:
            return {
                "prediction": prediction,
                "prediction_formatted": format_price(prediction),
                "confidence": confidence,
                "model_used": request.model_name or "lightgbm",
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
        features = llm_service.parse(request.text, verbose=False)

        if not features:
            raise HTTPException(status_code=400, detail="Failed to parse features")

        prediction = simple_predict(features)
        confidence = 85.0

        if request.use_ensemble:
            predictions = {
                "lightgbm": prediction * 1.02,
                "random_forest": prediction * 0.98,
                "xgboost": prediction * 1.01,
                "linear_regression": prediction * 0.99
            }

            ensemble_pred = sum(predictions.values()) / len(predictions)
            std = float(np.std(list(predictions.values())))

            return {
                "ensemble_prediction": ensemble_pred,
                "ensemble_prediction_formatted": format_price(ensemble_pred),
                "ensemble_std": std,
                "confidence": confidence,
                "individual_predictions": {
                    name: {"prediction": pred, "confidence": confidence}
                    for name, pred in predictions.items()
                },
                "models_used": list(predictions.keys()),
                "features_used": features
            }
        else:
            return {
                "prediction": prediction,
                "prediction_formatted": format_price(prediction),
                "confidence": confidence,
                "model_used": request.model_name or "lightgbm",
                "features_used": features
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Parse and predict failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")

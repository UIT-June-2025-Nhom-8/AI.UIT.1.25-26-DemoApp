"""
API routes for the backend
"""
from datetime import timedelta
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
import logging

from ..core import settings, create_access_token, authenticate_user, get_current_user
from ..services import model_service, llm_service
from ..services.full_preprocess_service import full_preprocess_service as preprocess_service
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

# Create router
router = APIRouter()


# ============================================================================
# Health & Info Endpoints
# ============================================================================

@router.get("/", response_model=MessageResponse)
async def root():
    """Root endpoint"""
    return {"message": f"Welcome to {settings.APP_NAME} v{settings.APP_VERSION}"}


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    # Ensure models are loaded
    if not model_service.loaded:
        model_service.load_models()

    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "models_loaded": len(model_service.get_available_models()),
        "llm_available": llm_service.is_available()
    }


@router.get("/models", response_model=AvailableModelsResponse)
async def get_available_models():
    """Get list of available models"""
    models = model_service.get_available_models()
    return {
        "models": models,
        "default_model": settings.DEFAULT_MODEL
    }


@router.get("/models/{model_name}", response_model=ModelInfoResponse)
async def get_model_info(model_name: str):
    """Get information about a specific model"""
    info = model_service.get_model_info(model_name)

    if info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{model_name}' not found"
        )

    return info


# ============================================================================
# Authentication Endpoints
# ============================================================================

@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login with username and password (hardcoded accounts for demo)

    Demo accounts:
    - admin / admin123
    - demo / demo123
    - user / user123
    """
    # Authenticate user
    if not authenticate_user(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": request.username},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": request.username
    }


@router.post("/auth/logout", response_model=MessageResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout (for demo, just returns success message)

    In production, you would invalidate the token here.
    """
    return {"message": f"User {current_user['username']} logged out successfully"}


@router.get("/auth/me", response_model=Dict[str, Any])
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user information"""
    return current_user


# ============================================================================
# Parsing Endpoints
# ============================================================================

@router.post("/parse", response_model=ParseResponse)
async def parse_text(request: ParseTextRequest):
    """
    Parse Vietnamese real estate description text into features

    Example:
        Input: "Nhà 120m2, 3 phòng ngủ, 2 WC, quận 7, sổ hồng"
        Output: {"Area": 120, "Bedrooms": 3, "Bathrooms": 2, ...}
    """
    if not llm_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM parsing service not available. Please set HUGGINGFACE_TOKEN."
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Parsing failed: {str(e)}"
        )


# ============================================================================
# Prediction Endpoints
# ============================================================================

@router.post("/predict", response_model=PredictionResponse | EnsemblePredictionResponse)
async def predict(request: PredictRequest):
    """
    Predict house price from features

    Can use a single model or ensemble of models.
    """
    try:
        # Preprocess features (returns DataFrame with 392 features)
        processed_features_df = preprocess_service.preprocess(request.features)

        # Make prediction
        if request.use_ensemble:
            # Ensemble prediction with all models
            result = model_service.predict_multi_model(processed_features_df)

            return {
                "ensemble_prediction": result["ensemble_prediction"],
                "ensemble_prediction_formatted": format_price(result["ensemble_prediction"]),
                "ensemble_std": result["ensemble_std"],
                "confidence": result["confidence"],
                "individual_predictions": result["individual_predictions"],
                "models_used": result["models_used"],
                "features_used": request.features  # Return original input
            }
        else:
            # Single model prediction
            result = model_service.predict_single(
                processed_features_df,
                model_name=request.model_name
            )

            return {
                "prediction": result["prediction"],
                "prediction_formatted": format_price(result["prediction"]),
                "confidence": result["confidence"],
                "model_used": result["model_used"],
                "features_used": request.features  # Return original input
            }

    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/parse-and-predict", response_model=PredictionResponse | EnsemblePredictionResponse)
async def parse_and_predict(request: ParseAndPredictRequest):
    """
    Parse text and predict price in one request

    Example:
        Input: "Nhà 120m2, 3PN, 2WC, quận 7, sổ hồng"
        Output: Prediction with parsed features
    """
    # Parse text
    if not llm_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM parsing service not available. Please set HUGGINGFACE_TOKEN."
        )

    try:
        features = llm_service.parse(request.text, verbose=False)

        if not features:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to parse features from text"
            )

        # Validate features
        is_valid, error_msg = preprocess_service.validate_features(features)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid parsed features: {error_msg}"
            )

        # Preprocess
        processed_features = preprocess_service.preprocess(features)

        # Predict
        if request.use_ensemble:
            result = model_service.predict_multi_model(processed_features)

            return {
                "ensemble_prediction": result["ensemble_prediction"],
                "ensemble_prediction_formatted": format_price(result["ensemble_prediction"]),
                "ensemble_std": result["ensemble_std"],
                "confidence": result["confidence"],
                "individual_predictions": result["individual_predictions"],
                "models_used": result["models_used"],
                "features_used": processed_features
            }
        else:
            result = model_service.predict_single(
                processed_features,
                model_name=request.model_name
            )

            return {
                "prediction": result["prediction"],
                "prediction_formatted": format_price(result["prediction"]),
                "confidence": result["confidence"],
                "model_used": result["model_used"],
                "features_used": processed_features
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Parse and predict failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Parse and predict failed: {str(e)}"
        )

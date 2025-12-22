"""
Model Service - Load and use trained ML models for prediction
"""
import joblib
import numpy as np
import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging

from ..core.config import settings


logger = logging.getLogger(__name__)


class ModelService:
    """Service for loading and using trained ML models"""

    def __init__(self):
        """Initialize model service"""
        self.models: Dict[str, Any] = {}
        self.model_metadata: Dict[str, dict] = {}
        self.loaded = False

    def load_models(self) -> None:
        """Load all available models from disk"""
        if self.loaded:
            logger.info("Models already loaded")
            return

        logger.info(f"Loading models from {settings.MODELS_DIR}")

        for model_name, model_file in settings.MODEL_FILES.items():
            try:
                model_path = settings.MODELS_DIR / model_file
                metadata_path = settings.MODELS_DIR / model_file.replace('.pkl', '_metadata.json')

                if not model_path.exists():
                    logger.warning(f"Model file not found: {model_path}")
                    continue

                # Load model
                logger.info(f"Loading {model_name} from {model_path}")
                self.models[model_name] = joblib.load(model_path)

                # Load metadata if exists
                if metadata_path.exists():
                    with open(metadata_path, 'r') as f:
                        self.model_metadata[model_name] = json.load(f)
                    logger.info(f"Loaded metadata for {model_name}")
                else:
                    logger.warning(f"Metadata not found for {model_name}")
                    self.model_metadata[model_name] = {}

                logger.info(f"✓ Loaded {model_name}")

            except Exception as e:
                logger.error(f"Failed to load {model_name}: {str(e)}")
                continue

        self.loaded = True
        logger.info(f"Loaded {len(self.models)} models: {list(self.models.keys())}")

    def get_available_models(self) -> List[str]:
        """Get list of available model names"""
        if not self.loaded:
            self.load_models()
        return list(self.models.keys())

    def get_model_info(self, model_name: str) -> Optional[dict]:
        """
        Get information about a specific model

        Args:
            model_name: Name of the model

        Returns:
            Model metadata or None if not found
        """
        if not self.loaded:
            self.load_models()

        if model_name not in self.models:
            return None

        info = {
            "name": model_name,
            "available": True,
            "metadata": self.model_metadata.get(model_name, {})
        }

        return info

    def predict_single(
        self,
        features: Dict[str, Any],
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make prediction for a single input

        Args:
            features: Dictionary of features
            model_name: Name of model to use (default: use default model)

        Returns:
            Dictionary with prediction results
        """
        if not self.loaded:
            self.load_models()

        # Use default model if not specified
        if model_name is None:
            model_name = settings.DEFAULT_MODEL

        # Check if model exists
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found. Available: {self.get_available_models()}")

        # Convert features to DataFrame (single row)
        feature_df = pd.DataFrame([features])

        # Get model
        model = self.models[model_name]

        # Make prediction
        try:
            prediction = model.predict(feature_df)[0]

            # Convert numpy types to Python types
            prediction = float(prediction)

            result = {
                "prediction": prediction,
                "model_used": model_name,
                "confidence": self._calculate_confidence(prediction, model_name),
                "features_used": features
            }

            return result

        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise ValueError(f"Prediction failed: {str(e)}")

    def predict_multi_model(
        self,
        features: Dict[str, Any],
        model_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Make predictions using multiple models and return ensemble results

        Args:
            features: Dictionary of features
            model_names: List of model names to use (None = use all)

        Returns:
            Dictionary with predictions from all models and ensemble result
        """
        if not self.loaded:
            self.load_models()

        # Use all models if not specified
        if model_names is None:
            model_names = self.get_available_models()

        # Validate models
        available = self.get_available_models()
        model_names = [m for m in model_names if m in available]

        if not model_names:
            raise ValueError(f"No valid models specified. Available: {available}")

        # Get predictions from each model
        predictions = {}
        all_preds = []

        for model_name in model_names:
            try:
                result = self.predict_single(features, model_name)
                predictions[model_name] = result
                all_preds.append(result['prediction'])
            except Exception as e:
                logger.error(f"Prediction with {model_name} failed: {str(e)}")
                continue

        if not all_preds:
            raise ValueError("All model predictions failed")

        # Calculate ensemble prediction (average)
        ensemble_prediction = float(np.mean(all_preds))
        ensemble_std = float(np.std(all_preds))

        # Calculate confidence (inverse of coefficient of variation)
        if ensemble_prediction > 0:
            cv = ensemble_std / ensemble_prediction
            confidence = max(0, min(100, (1 - cv) * 100))
        else:
            confidence = 50.0

        result = {
            "ensemble_prediction": ensemble_prediction,
            "ensemble_std": ensemble_std,
            "confidence": confidence,
            "individual_predictions": predictions,
            "models_used": model_names,
            "features_used": features
        }

        return result

    def _calculate_confidence(
        self,
        prediction: float,
        model_name: str
    ) -> float:
        """
        Calculate confidence score for a prediction

        For demo purposes, this returns a simple confidence score.
        In production, you might use model-specific methods like
        prediction intervals, standard errors, etc.

        Args:
            prediction: Predicted value
            model_name: Name of model used

        Returns:
            Confidence score (0-100)
        """
        # Simple confidence based on prediction magnitude
        # This is a placeholder - you should implement proper confidence estimation
        # based on your models (e.g., using prediction intervals, std, etc.)

        # For now, return a fixed high confidence for demo
        return 85.0

    def get_feature_importance(
        self,
        model_name: Optional[str] = None
    ) -> Optional[Dict[str, float]]:
        """
        Get feature importance from a model

        Args:
            model_name: Name of model (default: use default model)

        Returns:
            Dictionary of feature importances or None
        """
        if not self.loaded:
            self.load_models()

        if model_name is None:
            model_name = settings.DEFAULT_MODEL

        if model_name not in self.models:
            return None

        model = self.models[model_name]
        metadata = self.model_metadata.get(model_name, {})

        # Try to get feature importance
        feature_names = metadata.get('feature_names', [])

        if hasattr(model, 'feature_importances_') and feature_names:
            importances = model.feature_importances_
            feature_importance = dict(zip(feature_names, importances.tolist()))
            # Sort by importance
            feature_importance = dict(sorted(
                feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            ))
            return feature_importance

        return None


# Global model service instance
model_service = ModelService()

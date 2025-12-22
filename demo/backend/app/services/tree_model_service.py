"""
Tree Model Service - Load and use trained tree-based ML models for prediction
Supports: LightGBM, XGBoost, Random Forest
"""
import joblib
import numpy as np
import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

# Expected feature names (must match training)
# IMPORTANT: Order must match the trained models from notebooks/models/saved_models
EXPECTED_FEATURES = [
    "Area", "Frontage", "Access Road", "House direction", "Balcony direction",
    "Floors", "Bedrooms", "Bathrooms", "Legal status", "Furniture state",
    "new_has_balcony_direction", "new_has_house_direction",
    "new_city", "new_district", "new_street_ward",          # Fixed order
    "new_has_access_road", "has_frontage",                   # Fixed order
    "new_bathroom_bedroom_ratio", "new_total_rooms", "new_is_large_house",
    "new_avg_room_size", "new_is_luxury", "new_is_multi_story", "Area_binned",
    "area_x_bathrooms", "area_x_bedrooms", "area_x_floors", "bedrooms_x_bathrooms",
    "bedrooms_x_floors", "luxury_score", "area_in_hồ_chí_minh", "area_in_hà_nội",
    "area_in_bình_dương", "area_in_đà_nẵng", "room_density", "access_quality",
    "new_district_area_mean", "new_district_area_median", "new_district_area_std",
    "new_district_sample_count", "new_district_tier"
]


class TreeModelService:
    """Service for loading and using tree-based ML models"""

    def __init__(self, models_dir: Optional[Path] = None):
        """
        Initialize model service.
        
        Args:
            models_dir: Directory containing trained model files
        """
        if models_dir is None:
            # Default to notebooks/models directory (where models are saved)
            models_dir = Path(__file__).parent.parent.parent.parent.parent / "notebooks" / "models"
        
        self.models_dir = Path(models_dir)
        self.models: Dict[str, Any] = {}
        self.model_metadata: Dict[str, dict] = {}
        self.loaded = False
        
        logger.info(f"TreeModelService initialized with models_dir: {self.models_dir}")

    def load_models(self) -> None:
        """Load all available tree-based models from disk"""
        if self.loaded:
            logger.info("Models already loaded")
            return

        logger.info(f"Loading models from {self.models_dir}")
        
        if not self.models_dir.exists():
            logger.warning(f"Models directory not found: {self.models_dir}")
            return

        # Find and load model files
        model_patterns = {
            "lightgbm": "lightgbm_regressor_*.pkl",
            "xgboost": "xgboost_regressor_*.pkl", 
            "random_forest": "random_forest_regressor_*.pkl"
        }

        for model_name, pattern in model_patterns.items():
            try:
                # Find matching files
                model_files = list(self.models_dir.glob(pattern))
                if not model_files:
                    logger.warning(f"No model file found for {model_name} with pattern {pattern}")
                    continue
                
                # Use the most recent one (sorted by name, which includes timestamp)
                model_path = sorted(model_files)[-1]
                metadata_path = model_path.with_suffix('.json').with_name(
                    model_path.stem + '_metadata.json'
                )

                # Load model
                logger.info(f"Loading {model_name} from {model_path}")
                self.models[model_name] = joblib.load(model_path)

                # Load metadata if exists
                if metadata_path.exists():
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        self.model_metadata[model_name] = json.load(f)
                    logger.info(f"Loaded metadata for {model_name}")
                else:
                    logger.warning(f"Metadata not found for {model_name}")
                    self.model_metadata[model_name] = {}

                logger.info(f"✓ Loaded {model_name}")

            except Exception as e:
                logger.error(f"Failed to load {model_name}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

        self.loaded = True
        logger.info(f"Loaded {len(self.models)} models: {list(self.models.keys())}")

    def get_available_models(self) -> List[str]:
        """Get list of available model names"""
        if not self.loaded:
            self.load_models()
        return list(self.models.keys())

    def get_model_info(self, model_name: str) -> Optional[dict]:
        """Get information about a specific model"""
        if not self.loaded:
            self.load_models()

        if model_name not in self.models:
            return None

        return {
            "name": model_name,
            "available": True,
            "metadata": self.model_metadata.get(model_name, {}),
            "expected_features": len(EXPECTED_FEATURES)
        }

    def predict(self, features_df: pd.DataFrame, model_name: str = "lightgbm") -> Dict[str, Any]:
        """
        Make prediction using the specified model.

        Args:
            features_df: DataFrame with preprocessed features (41 columns)
            model_name: Name of model to use

        Returns:
            Dictionary with prediction results
        """
        if not self.loaded:
            self.load_models()

        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found. Available: {self.get_available_models()}")

        model = self.models[model_name]

        try:
            # Ensure features are in correct order
            if set(features_df.columns) != set(EXPECTED_FEATURES):
                missing = set(EXPECTED_FEATURES) - set(features_df.columns)
                extra = set(features_df.columns) - set(EXPECTED_FEATURES)
                if missing:
                    logger.warning(f"Missing features: {missing}")
                if extra:
                    logger.warning(f"Extra features: {extra}")

            # Reorder columns to match expected order
            features_df = features_df[EXPECTED_FEATURES].copy()

            # LightGBM uses underscores instead of spaces in feature names
            # Rename columns for LightGBM compatibility
            if model_name == "lightgbm":
                rename_map = {
                    "Access Road": "Access_Road",
                    "House direction": "House_direction",
                    "Balcony direction": "Balcony_direction",
                    "Legal status": "Legal_status",
                    "Furniture state": "Furniture_state"
                }
                features_df = features_df.rename(columns=rename_map)

            # Make prediction
            prediction = model.predict(features_df)[0]
            prediction = float(prediction)

            # Calculate confidence based on model metadata
            metadata = self.model_metadata.get(model_name, {})
            r2_score = metadata.get('r2_score', 0.85)
            confidence = max(70, min(95, r2_score * 100))

            return {
                "prediction": prediction,
                "model_used": model_name,
                "confidence": confidence,
                "feature_count": len(features_df.columns)
            }

        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise ValueError(f"Prediction failed: {str(e)}")

    def predict_all_models(self, features_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Make predictions using all available models and return ensemble result.
        
        Args:
            features_df: DataFrame with preprocessed features
            
        Returns:
            Dictionary with ensemble and individual predictions
        """
        if not self.loaded:
            self.load_models()

        predictions = {}
        confidences = {}
        
        for model_name in self.models.keys():
            try:
                result = self.predict(features_df.copy(), model_name)
                predictions[model_name] = result["prediction"]
                confidences[model_name] = result["confidence"]
            except Exception as e:
                logger.error(f"Failed to predict with {model_name}: {e}")
                continue

        if not predictions:
            raise ValueError("No model could make a prediction")

        # Calculate ensemble (simple average)
        ensemble_pred = sum(predictions.values()) / len(predictions)
        ensemble_std = float(np.std(list(predictions.values())))
        ensemble_confidence = sum(confidences.values()) / len(confidences)

        return {
            "ensemble_prediction": ensemble_pred,
            "ensemble_std": ensemble_std,
            "ensemble_confidence": ensemble_confidence,
            "individual_predictions": {
                name: {"prediction": pred, "confidence": confidences[name]}
                for name, pred in predictions.items()
            },
            "models_used": list(predictions.keys())
        }


# Singleton instance
_model_service: Optional[TreeModelService] = None


def get_model_service() -> TreeModelService:
    """Get or create model service singleton"""
    global _model_service
    if _model_service is None:
        # Use models from demo/backend/models directory
        models_dir = Path(__file__).parent.parent.parent / "models"
        _model_service = TreeModelService(models_dir=models_dir)
        _model_service.load_models()
    return _model_service

"""
Model Implementations
Author: CS106.TTNT Final Project

Tree-based models optimized for label-encoded features
"""

from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import lightgbm as lgb
from typing import Dict, Any

from .base_model import BaseModel

# Linear Regression REMOVED
# Tree-based models below are optimized for the tree_optimized_preprocessing pipeline
# which uses label encoding instead of one-hot encoding


class RandomForestModel(BaseModel):
    """
    Random Forest Regressor Model
    """

    def __init__(self, model_params: Dict[str, Any], config: Dict[str, Any]):
        super().__init__("Random Forest Regressor", model_params, config)

    def build_model(self):
        """Build Random Forest model"""
        self.model = RandomForestRegressor(**self.model_params)
        return self.model


class XGBoostModel(BaseModel):
    """
    XGBoost Regressor Model
    """

    def __init__(self, model_params: Dict[str, Any], config: Dict[str, Any]):
        super().__init__("XGBoost Regressor", model_params, config)

    def build_model(self):
        """Build XGBoost model"""
        self.model = xgb.XGBRegressor(**self.model_params)
        return self.model


class LightGBMModel(BaseModel):
    """
    LightGBM Regressor Model
    """

    def __init__(self, model_params: Dict[str, Any], config: Dict[str, Any]):
        super().__init__("LightGBM Regressor", model_params, config)

    def build_model(self):
        """Build LightGBM model"""
        self.model = lgb.LGBMRegressor(**self.model_params)
        return self.model


# Model factory - Tree-based models only
# Optimized for label-encoded features from tree_optimized_preprocessing.py
MODEL_REGISTRY = {
    'random_forest': RandomForestModel,
    'xgboost': XGBoostModel,
    'lightgbm': LightGBMModel
}


def create_model(model_name: str, config: Dict[str, Any]) -> BaseModel:
    """
    Factory function to create model instance

    Args:
        model_name: Name of model from config (e.g., 'random_forest')
        config: Full configuration dictionary

    Returns:
        Model instance

    Raises:
        ValueError: If model name not found
    """
    if model_name not in MODEL_REGISTRY:
        raise ValueError(f"Model '{model_name}' not found. Available: {list(MODEL_REGISTRY.keys())}")

    model_config = config['models'][model_name]
    model_params = model_config['params']

    model_class = MODEL_REGISTRY[model_name]
    return model_class(model_params, config)

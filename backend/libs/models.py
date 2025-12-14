"""
Model Implementations
Author: CS106.TTNT Final Project
"""

from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import lightgbm as lgb
from typing import Dict, Any

from .base_model import BaseModel


class LinearRegressionModel(BaseModel):
    """
    Ridge Regression Model (L2 Regularization)
    Note: For regression task, we use Ridge instead of Logistic Regression
    """

    def __init__(self, model_params: Dict[str, Any], config: Dict[str, Any]):
        super().__init__("Linear Regression (Ridge)", model_params, config)

    def build_model(self):
        """Build Ridge Regression model"""
        self.model = Ridge(**self.model_params)
        return self.model


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


# Model factory
MODEL_REGISTRY = {
    'linear_regression': LinearRegressionModel,
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

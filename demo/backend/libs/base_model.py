"""
Base Model Class for ML Pipeline
Author: CS106.TTNT Final Project
"""

from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple
import joblib
import json
from pathlib import Path
from datetime import datetime


class BaseModel(ABC):
    """
    Abstract base class for all models in the pipeline
    """

    def __init__(self, name: str, model_params: Dict[str, Any], config: Dict[str, Any]):
        """
        Initialize base model

        Args:
            name: Name of the model
            model_params: Parameters for the model
            config: Full configuration dictionary
        """
        self.name = name
        self.model_params = model_params
        self.config = config
        self.model = None
        self.is_trained = False
        self.training_time = None
        self.predictions = {}
        self.feature_names = None

    @abstractmethod
    def build_model(self):
        """Build the model with specified parameters"""
        pass

    def fit(self, X: pd.DataFrame, y: pd.Series) -> 'BaseModel':
        """
        Train the model

        Args:
            X: Training features
            y: Training target

        Returns:
            self
        """
        start_time = datetime.now()

        # Store feature names
        self.feature_names = X.columns.tolist()

        # Build model if not already built
        if self.model is None:
            self.build_model()

        # Train model
        print(f"Training {self.name}...")
        self.model.fit(X, y)

        # Calculate training time
        self.training_time = (datetime.now() - start_time).total_seconds()
        self.is_trained = True

        print(f"{self.name} trained in {self.training_time:.2f} seconds")

        return self

    def predict(self, X: pd.DataFrame, label: str = "test") -> np.ndarray:
        """
        Make predictions

        Args:
            X: Features to predict
            label: Label for this prediction (e.g., 'train', 'test', 'val')

        Returns:
            Predictions array
        """
        if not self.is_trained:
            raise ValueError(f"{self.name} is not trained yet!")

        predictions = self.model.predict(X)
        self.predictions[label] = predictions

        return predictions

    def get_feature_importance(self) -> Optional[pd.DataFrame]:
        """
        Get feature importance if available

        Returns:
            DataFrame with feature importance or None
        """
        if not self.is_trained:
            return None

        # Check if model has feature_importances_ attribute
        if hasattr(self.model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.model.feature_importances_
            })
            importance_df = importance_df.sort_values('importance', ascending=False)
            return importance_df

        # Check if model has coef_ attribute (for linear models)
        elif hasattr(self.model, 'coef_'):
            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'coefficient': np.abs(self.model.coef_)
            })
            importance_df = importance_df.sort_values('coefficient', ascending=False)
            return importance_df

        return None

    def save_model(self, save_dir: str) -> str:
        """
        Save model to disk

        Args:
            save_dir: Directory to save model

        Returns:
            Path to saved model
        """
        if not self.is_trained:
            raise ValueError(f"{self.name} is not trained yet!")

        # Create directory if not exists
        Path(save_dir).mkdir(parents=True, exist_ok=True)

        # Create filename with timestamp
        timestamp = datetime.now().strftime(self.config['output']['timestamp_format'])
        model_name = self.name.lower().replace(' ', '_')
        model_path = f"{save_dir}/{model_name}_{timestamp}.pkl"

        # Save model
        joblib.dump(self.model, model_path)

        # Save metadata
        metadata = {
            'name': self.name,
            'params': self.model_params,
            'feature_names': self.feature_names,
            'training_time': self.training_time,
            'timestamp': timestamp
        }

        metadata_path = f"{save_dir}/{model_name}_{timestamp}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)

        print(f"{self.name} saved to {model_path}")

        return model_path

    def load_model(self, model_path: str):
        """
        Load model from disk

        Args:
            model_path: Path to saved model
        """
        self.model = joblib.load(model_path)
        self.is_trained = True

        # Try to load metadata
        metadata_path = model_path.replace('.pkl', '_metadata.json')
        if Path(metadata_path).exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                self.feature_names = metadata.get('feature_names')
                self.training_time = metadata.get('training_time')

        print(f"{self.name} loaded from {model_path}")

    def get_params(self) -> Dict[str, Any]:
        """
        Get model parameters

        Returns:
            Dictionary of parameters
        """
        if self.model is None:
            return self.model_params
        return self.model.get_params()

    def set_params(self, **params):
        """
        Set model parameters

        Args:
            **params: Parameters to set
        """
        if self.model is not None:
            self.model.set_params(**params)
        self.model_params.update(params)

    def __repr__(self) -> str:
        """String representation"""
        status = "Trained" if self.is_trained else "Not Trained"
        return f"{self.name} ({status})"

    def get_summary(self) -> Dict[str, Any]:
        """
        Get model summary

        Returns:
            Dictionary with model summary
        """
        summary = {
            'name': self.name,
            'is_trained': self.is_trained,
            'training_time': self.training_time,
            'params': self.model_params
        }

        if self.feature_names:
            summary['n_features'] = len(self.feature_names)

        return summary

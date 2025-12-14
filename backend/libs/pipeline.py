"""
ML Pipeline for Model Training and Evaluation
Author: CS106.TTNT Final Project
"""

import numpy as np
import pandas as pd
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
import warnings
warnings.filterwarnings('ignore')

from .models import create_model, MODEL_REGISTRY
from .metrics import calculate_metrics, compare_models, create_metrics_report
from .visualization import create_report_figures


class MLPipeline:
    """
    Complete ML Pipeline for training and evaluating multiple models
    """

    def __init__(self, config_path: str):
        """
        Initialize pipeline with configuration

        Args:
            config_path: Path to YAML config file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.models = {}
        self.results = {}
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.feature_names = None

        # Create output directories
        self._create_output_dirs()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        print(f"Configuration loaded from {self.config_path}")
        return config

    def _create_output_dirs(self):
        """Create output directories if they don't exist"""
        output_config = self.config['output']
        for dir_key in ['models_dir', 'results_dir', 'reports_dir', 'figures_dir']:
            dir_path = output_config[dir_key]
            Path(dir_path).mkdir(parents=True, exist_ok=True)

    def load_data(self, data_path: Optional[str] = None) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Load and prepare data

        Args:
            data_path: Path to dataset (if None, use config)

        Returns:
            X, y tuple
        """
        if data_path is None:
            data_path = self.config['dataset']['train_path']

        print(f"Loading data from {data_path}...")
        df = pd.read_csv(data_path)

        # Get target column
        target_col = self.config['dataset']['target_column']

        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in dataset!")

        # Separate features and target
        X = df.drop(columns=[target_col])
        y = df[target_col]

        # Handle categorical columns (skip if data is already preprocessed)
        skip_preprocessing = self.config['dataset'].get('skip_preprocessing', False)
        if not skip_preprocessing:
            X = self._preprocess_features(X)
        else:
            print("Skipping preprocessing - using pre-processed data...")
            # Convert all columns to numeric (handle one-hot encoded columns stored as strings)
            non_numeric = X.select_dtypes(exclude=[np.number]).columns.tolist()
            if non_numeric:
                print(f"  Converting {len(non_numeric)} non-numeric columns to numeric...")
                for col in non_numeric:
                    # Convert boolean/string columns to int
                    X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0).astype(int)
                print(f"  ✓ Converted all columns to numeric")

            # Verify all columns are now numeric
            remaining_non_numeric = X.select_dtypes(exclude=[np.number]).columns.tolist()
            if remaining_non_numeric:
                print(f"  Warning: Still have non-numeric columns: {remaining_non_numeric}")
                print("  Applying full preprocessing...")
                X = self._preprocess_features(X)
            else:
                print(f"  ✓ All {X.shape[1]} features are numeric")

        # Apply log transform if specified
        if self.config['dataset'].get('use_log_transform', False):
            print("Applying log transformation to target variable...")
            y = np.log1p(y)

        print(f"Data loaded: {X.shape[0]} samples, {X.shape[1]} features")
        self.feature_names = X.columns.tolist()

        return X, y

    def _preprocess_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess features: handle categorical columns and missing values

        Args:
            X: Features DataFrame

        Returns:
            Preprocessed DataFrame with only numeric features
        """
        from sklearn.preprocessing import LabelEncoder

        print("Preprocessing features...")

        # Columns to drop (used for feature engineering, now redundant)
        columns_to_drop = [
            'Address',  # Already encoded into new_city, new_district, new_street_ward
        ]

        # Drop redundant columns if they exist
        existing_cols_to_drop = [col for col in columns_to_drop if col in X.columns]
        if existing_cols_to_drop:
            print(f"  Dropping redundant columns: {existing_cols_to_drop}")
            X = X.drop(columns=existing_cols_to_drop)

        # Identify categorical columns (object dtype)
        categorical_cols = X.select_dtypes(include=['object']).columns.tolist()

        if categorical_cols:
            print(f"  Encoding {len(categorical_cols)} categorical columns: {categorical_cols}")

            # Apply label encoding to each categorical column
            for col in categorical_cols:
                # Handle NaN values by filling with a placeholder
                X[col] = X[col].fillna('Unknown')
                # Create a new encoder for each column to ensure consistent encoding
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col])
                print(f"    - {col}: {len(le.classes_)} unique values")

        # Handle missing values in numeric columns
        numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        missing_counts = X[numeric_cols].isnull().sum()
        cols_with_missing = missing_counts[missing_counts > 0]

        if len(cols_with_missing) > 0:
            print(f"  Filling missing values in {len(cols_with_missing)} numeric columns:")
            for col in cols_with_missing.index:
                n_missing = cols_with_missing[col]
                # Fill with median for numeric columns
                X[col] = X[col].fillna(X[col].median())
                print(f"    - {col}: filled {n_missing} missing values with median")

        # Verify all columns are now numeric
        non_numeric = X.select_dtypes(exclude=[np.number]).columns.tolist()
        if non_numeric:
            raise ValueError(f"Non-numeric columns still present after preprocessing: {non_numeric}")

        # Verify no missing values remain
        remaining_missing = X.isnull().sum().sum()
        if remaining_missing > 0:
            raise ValueError(f"Missing values still present after preprocessing: {remaining_missing}")

        print(f"  ✓ All features are now numeric with no missing values")

        return X

    def split_data(self, X: pd.DataFrame, y: pd.Series):
        """
        Split data into train and test sets

        Args:
            X: Features
            y: Target
        """
        test_size = self.config['dataset']['test_size']
        random_state = self.config['dataset']['random_state']

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        print(f"Data split: {len(self.X_train)} train, {len(self.X_test)} test")

    def initialize_models(self, model_names: Optional[List[str]] = None):
        """
        Initialize models from config

        Args:
            model_names: List of model names to initialize (if None, use all enabled)
        """
        models_config = self.config['models']

        if model_names is None:
            # Get all enabled models
            model_names = [name for name, cfg in models_config.items() if cfg.get('enabled', True)]

        print(f"Initializing {len(model_names)} models...")

        for model_name in model_names:
            if model_name not in MODEL_REGISTRY:
                print(f"Warning: Model '{model_name}' not found in registry. Skipping.")
                continue

            print(f"  - {models_config[model_name]['name']}")
            self.models[model_name] = create_model(model_name, self.config)

    def train_model(self, model_name: str, tune_hyperparameters: bool = False):
        """
        Train a single model

        Args:
            model_name: Name of model to train
            tune_hyperparameters: Whether to perform hyperparameter tuning
        """
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not initialized!")

        model = self.models[model_name]
        model_config = self.config['models'][model_name]

        print(f"\n{'='*80}")
        print(f"Training {model.name}...")
        print(f"{'='*80}")

        # Hyperparameter tuning
        if tune_hyperparameters and model_config['hyperparameter_tuning']['enabled']:
            print("Performing hyperparameter tuning...")
            best_params = self._tune_hyperparameters(model_name)
            model.set_params(**best_params)
            print(f"Best parameters: {best_params}")

        # Train model
        model.fit(self.X_train, self.y_train)

        # Make predictions
        y_train_pred = model.predict(self.X_train, label='train')
        y_test_pred = model.predict(self.X_test, label='test')

        # Inverse transform if log was used
        if self.config['dataset'].get('use_log_transform', False):
            y_train_true = np.expm1(self.y_train)
            y_test_true = np.expm1(self.y_test)
            y_train_pred = np.expm1(y_train_pred)
            y_test_pred = np.expm1(y_test_pred)
        else:
            y_train_true = self.y_train
            y_test_true = self.y_test

        # Calculate metrics (pass n_features for correct adjusted R² calculation)
        train_metrics = calculate_metrics(y_train_true, y_train_pred, self.X_train.shape[1])
        test_metrics = calculate_metrics(y_test_true, y_test_pred, self.X_test.shape[1])

        # Get feature importance
        feature_importance = model.get_feature_importance()

        # Store results
        self.results[model_name] = {
            'model': model,
            'train_metrics': train_metrics,
            'test_metrics': test_metrics,
            'metrics': test_metrics,  # Default to test metrics
            'training_time': model.training_time,
            'y_test': y_test_true,
            'y_pred': y_test_pred,
            'feature_importance': feature_importance
        }

        # Print results
        print(f"\nTraining completed in {model.training_time:.2f} seconds")
        print(f"\nTrain Metrics:")
        self._print_metrics(train_metrics)
        print(f"\nTest Metrics:")
        self._print_metrics(test_metrics)

    def _tune_hyperparameters(self, model_name: str) -> Dict[str, Any]:
        """
        Perform hyperparameter tuning

        Args:
            model_name: Name of model to tune

        Returns:
            Best parameters
        """
        model = self.models[model_name]
        tuning_config = self.config['models'][model_name]['hyperparameter_tuning']

        # Build model if not already built
        if model.model is None:
            model.build_model()

        method = tuning_config['method']
        cv = tuning_config['cv']

        if method == 'grid_search':
            param_grid = tuning_config['param_grid']
            search = GridSearchCV(
                model.model,
                param_grid,
                cv=cv,
                scoring=self.config['training']['scoring'],
                n_jobs=-1,
                verbose=1
            )
        elif method == 'random_search':
            param_distributions = tuning_config['param_distributions']
            n_iter = tuning_config['n_iter']
            search = RandomizedSearchCV(
                model.model,
                param_distributions,
                n_iter=n_iter,
                cv=cv,
                scoring=self.config['training']['scoring'],
                n_jobs=-1,
                verbose=1,
                random_state=self.config['dataset']['random_state']
            )
        else:
            raise ValueError(f"Unknown tuning method: {method}")

        search.fit(self.X_train, self.y_train)

        return search.best_params_

    def train_all_models(self, tune_hyperparameters: bool = False):
        """
        Train all initialized models

        Args:
            tune_hyperparameters: Whether to perform hyperparameter tuning
        """
        print(f"\n{'='*80}")
        print(f"TRAINING ALL MODELS")
        print(f"{'='*80}\n")

        for model_name in self.models.keys():
            self.train_model(model_name, tune_hyperparameters)

        print(f"\n{'='*80}")
        print(f"ALL MODELS TRAINED")
        print(f"{'='*80}\n")

    def _print_metrics(self, metrics: Dict[str, float]):
        """Print metrics in formatted way"""
        print(f"  R² Score:      {metrics['r2_score']:.4f}")
        print(f"  Adjusted R²:   {metrics['adjusted_r2']:.4f}")
        print(f"  RMSE:          {metrics['rmse']:.4f}")
        print(f"  MAE:           {metrics['mae']:.4f}")
        print(f"  MAPE:          {metrics['mape']:.2f}%")

    def compare_models(self) -> pd.DataFrame:
        """
        Compare all trained models

        Returns:
            Comparison DataFrame
        """
        if not self.results:
            raise ValueError("No models have been trained yet!")

        comparison_df = compare_models(self.results)
        print("\n" + "="*80)
        print("MODEL COMPARISON")
        print("="*80)
        print(comparison_df.to_string(index=False))

        return comparison_df

    def save_models(self):
        """Save all trained models"""
        if not self.config['output']['save_models']:
            return

        save_dir = self.config['output']['models_dir']
        print(f"\nSaving models to {save_dir}...")

        for model_name, result in self.results.items():
            model = result['model']
            model.save_model(save_dir)

    def save_results(self):
        """Save all results"""
        if not self.config['output']['save_results']:
            return

        results_dir = self.config['output']['results_dir']
        timestamp = datetime.now().strftime(self.config['output']['timestamp_format'])

        print(f"\nSaving results to {results_dir}...")

        # Save metrics
        metrics_data = {}
        for model_name, result in self.results.items():
            metrics_data[model_name] = {
                'train_metrics': result['train_metrics'],
                'test_metrics': result['test_metrics'],
                'training_time': result['training_time']
            }

        metrics_path = f"{results_dir}/metrics_{timestamp}.json"
        with open(metrics_path, 'w') as f:
            json.dump(metrics_data, f, indent=4)
        print(f"  Metrics saved to {metrics_path}")

        # Save comparison
        comparison_df = compare_models(self.results)
        comparison_path = f"{results_dir}/comparison_{timestamp}.csv"
        comparison_df.to_csv(comparison_path, index=False)
        print(f"  Comparison saved to {comparison_path}")

    def save_report(self):
        """Save text report"""
        if not self.config['output']['save_reports']:
            return

        reports_dir = self.config['output']['reports_dir']
        timestamp = datetime.now().strftime(self.config['output']['timestamp_format'])

        report = create_metrics_report(self.results)
        report_path = f"{reports_dir}/report_{timestamp}.txt"

        with open(report_path, 'w') as f:
            f.write(report)

        print(f"\nReport saved to {report_path}")

    def save_figures(self):
        """Save all visualization figures"""
        if not self.config['output']['save_figures']:
            return

        figures_dir = self.config['output']['figures_dir']
        timestamp = datetime.now().strftime(self.config['output']['timestamp_format'])
        save_dir = f"{figures_dir}/run_{timestamp}"

        comparison_df = compare_models(self.results)
        create_report_figures(self.results, comparison_df, save_dir)

    def run_pipeline(self,
                    data_path: Optional[str] = None,
                    model_names: Optional[List[str]] = None,
                    tune_hyperparameters: bool = False):
        """
        Run complete pipeline

        Args:
            data_path: Path to dataset
            model_names: List of models to train
            tune_hyperparameters: Whether to tune hyperparameters
        """
        print("\n" + "="*80)
        print("STARTING ML PIPELINE")
        print("="*80 + "\n")

        # Load data
        X, y = self.load_data(data_path)

        # Split data
        self.split_data(X, y)

        # Initialize models
        self.initialize_models(model_names)

        # Train models
        self.train_all_models(tune_hyperparameters)

        # Compare models
        self.compare_models()

        # Save everything
        self.save_models()
        self.save_results()
        self.save_report()
        self.save_figures()

        print("\n" + "="*80)
        print("PIPELINE COMPLETED")
        print("="*80 + "\n")

        return self.results

"""
Evaluation Metrics
Author: CS106.TTNT Final Project
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    r2_score,
    mean_squared_error,
    mean_absolute_error,
    mean_absolute_percentage_error
)
from typing import Dict, List, Any, Optional


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray, n_features: Optional[int] = None) -> Dict[str, float]:
    """
    Calculate all regression metrics

    Args:
        y_true: True values
        y_pred: Predicted values
        n_features: Number of features used in the model (for adjusted R² calculation)

    Returns:
        Dictionary of metrics
    """
    metrics = {
        'r2_score': r2_score(y_true, y_pred),
        'mse': mean_squared_error(y_true, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
        'mae': mean_absolute_error(y_true, y_pred),
        'mape': mean_absolute_percentage_error(y_true, y_pred) * 100  # Convert to percentage
    }

    # Additional metrics
    # Fix: Use passed n_features instead of y_pred.shape which is always 1 for 1D arrays
    if n_features is not None:
        metrics['adjusted_r2'] = calculate_adjusted_r2(
            metrics['r2_score'],
            len(y_true),
            n_features
        )
    else:
        # Fallback: use R² if n_features not provided
        metrics['adjusted_r2'] = metrics['r2_score']

    return metrics


def calculate_adjusted_r2(r2: float, n_samples: int, n_features: int) -> float:
    """
    Calculate adjusted R² score

    Args:
        r2: R² score
        n_samples: Number of samples
        n_features: Number of features

    Returns:
        Adjusted R² score
    """
    if n_samples - n_features - 1 <= 0:
        return r2

    adjusted_r2 = 1 - (1 - r2) * (n_samples - 1) / (n_samples - n_features - 1)
    return adjusted_r2


def calculate_residuals(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, np.ndarray]:
    """
    Calculate residuals and related statistics

    Args:
        y_true: True values
        y_pred: Predicted values

    Returns:
        Dictionary with residuals information
    """
    residuals = y_true - y_pred

    return {
        'residuals': residuals,
        'abs_residuals': np.abs(residuals),
        'squared_residuals': residuals ** 2,
        'mean_residual': np.mean(residuals),
        'std_residual': np.std(residuals),
        'min_residual': np.min(residuals),
        'max_residual': np.max(residuals)
    }


def compare_models(results: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    """
    Compare multiple models based on their metrics

    Args:
        results: Dictionary with model results
                 Format: {model_name: {'metrics': {...}, 'training_time': ...}}

    Returns:
        DataFrame with comparison
    """
    comparison_data = []

    for model_name, result in results.items():
        metrics = result.get('metrics', {})
        row = {
            'Model': model_name,
            'R² Score': metrics.get('r2_score', np.nan),
            'Adjusted R²': metrics.get('adjusted_r2', np.nan),
            'RMSE': metrics.get('rmse', np.nan),
            'MAE': metrics.get('mae', np.nan),
            'MAPE (%)': metrics.get('mape', np.nan),
            'Training Time (s)': result.get('training_time', np.nan)
        }
        comparison_data.append(row)

    df = pd.DataFrame(comparison_data)

    # Sort by R² score (descending)
    if 'R² Score' in df.columns:
        df = df.sort_values('R² Score', ascending=False)

    return df


def get_best_model(results: Dict[str, Dict[str, Any]], metric: str = 'r2_score') -> str:
    """
    Get the best model based on specified metric

    Args:
        results: Dictionary with model results
        metric: Metric to use for comparison (default: 'r2_score')

    Returns:
        Name of best model
    """
    best_score = -np.inf if metric in ['r2_score', 'adjusted_r2'] else np.inf
    best_model = None

    for model_name, result in results.items():
        metrics = result.get('metrics', {})
        score = metrics.get(metric, np.nan)

        if np.isnan(score):
            continue

        # For R² metrics, higher is better
        if metric in ['r2_score', 'adjusted_r2']:
            if score > best_score:
                best_score = score
                best_model = model_name
        # For error metrics, lower is better
        else:
            if score < best_score:
                best_score = score
                best_model = model_name

    return best_model


def create_metrics_report(results: Dict[str, Dict[str, Any]]) -> str:
    """
    Create a formatted text report of model metrics

    Args:
        results: Dictionary with model results

    Returns:
        Formatted report string
    """
    report_lines = [
        "=" * 80,
        "MODEL COMPARISON REPORT",
        "=" * 80,
        ""
    ]

    comparison_df = compare_models(results)

    report_lines.append(comparison_df.to_string(index=False))
    report_lines.append("")
    report_lines.append("=" * 80)

    # Best models
    report_lines.append("BEST MODELS BY METRIC:")
    report_lines.append("-" * 80)

    metrics_to_check = ['r2_score', 'rmse', 'mae', 'mape']
    for metric in metrics_to_check:
        best_model = get_best_model(results, metric)
        if best_model:
            report_lines.append(f"  {metric.upper():20s}: {best_model}")

    report_lines.append("=" * 80)

    return "\n".join(report_lines)


def evaluate_predictions(y_true: np.ndarray,
                        y_pred: np.ndarray,
                        model_name: str = "Model") -> Dict[str, Any]:
    """
    Complete evaluation of predictions

    Args:
        y_true: True values
        y_pred: Predicted values
        model_name: Name of the model

    Returns:
        Dictionary with all evaluation results
    """
    return {
        'model_name': model_name,
        'metrics': calculate_metrics(y_true, y_pred),
        'residuals': calculate_residuals(y_true, y_pred),
        'n_samples': len(y_true)
    }

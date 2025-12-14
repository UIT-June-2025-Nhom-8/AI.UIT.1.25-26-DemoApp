"""
Visualization Utilities
Author: CS106.TTNT Final Project
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def _save_figure(fig: plt.Figure, save_path: Optional[str]) -> None:
    """
    Save figure to file with consistent formatting.

    Args:
        fig: Figure to save
        save_path: Path to save figure (None to skip)
    """
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to {save_path}")


def plot_actual_vs_predicted(y_true: np.ndarray,
                            y_pred: np.ndarray,
                            model_name: str = "Model",
                            save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot actual vs predicted values

    Args:
        y_true: True values
        y_pred: Predicted values
        model_name: Name of the model
        save_path: Path to save figure

    Returns:
        Figure object
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Scatter plot
    ax.scatter(y_true, y_pred, alpha=0.5, s=20)

    # Perfect prediction line
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')

    # Labels and title
    ax.set_xlabel('Actual Price (billion VND)', fontsize=12)
    ax.set_ylabel('Predicted Price (billion VND)', fontsize=12)
    ax.set_title(f'Actual vs Predicted - {model_name}', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    _save_figure(fig, save_path)

    return fig


def plot_residuals(y_true: np.ndarray,
                  y_pred: np.ndarray,
                  model_name: str = "Model",
                  save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot residuals distribution and residual plot

    Args:
        y_true: True values
        y_pred: Predicted values
        model_name: Name of the model
        save_path: Path to save figure

    Returns:
        Figure object
    """
    residuals = y_true - y_pred

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    # Residual plot
    axes[0].scatter(y_pred, residuals, alpha=0.5, s=20)
    axes[0].axhline(y=0, color='r', linestyle='--', lw=2)
    axes[0].set_xlabel('Predicted Price (billion VND)', fontsize=12)
    axes[0].set_ylabel('Residuals', fontsize=12)
    axes[0].set_title(f'Residual Plot - {model_name}', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)

    # Residuals distribution
    axes[1].hist(residuals, bins=50, edgecolor='black', alpha=0.7)
    axes[1].axvline(x=0, color='r', linestyle='--', lw=2)
    axes[1].set_xlabel('Residuals', fontsize=12)
    axes[1].set_ylabel('Frequency', fontsize=12)
    axes[1].set_title(f'Residuals Distribution - {model_name}', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    _save_figure(fig, save_path)

    return fig


def plot_feature_importance(importance_df: pd.DataFrame,
                           model_name: str = "Model",
                           top_n: int = 15,
                           save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot feature importance

    Args:
        importance_df: DataFrame with features and importance/coefficient
        model_name: Name of the model
        top_n: Number of top features to show
        save_path: Path to save figure

    Returns:
        Figure object
    """
    # Get top N features
    top_features = importance_df.head(top_n).copy()

    # Determine column name (importance or coefficient)
    value_col = 'importance' if 'importance' in top_features.columns else 'coefficient'

    fig, ax = plt.subplots(figsize=(10, 8))

    # Horizontal bar plot
    bars = ax.barh(range(len(top_features)), top_features[value_col])

    # Color bars
    colors = plt.cm.viridis(np.linspace(0, 1, len(top_features)))
    for bar, color in zip(bars, colors):
        bar.set_color(color)

    # Labels
    ax.set_yticks(range(len(top_features)))
    ax.set_yticklabels(top_features['feature'])
    ax.set_xlabel(value_col.capitalize(), fontsize=12)
    ax.set_title(f'Top {top_n} Feature {value_col.capitalize()} - {model_name}',
                fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    _save_figure(fig, save_path)

    return fig


def plot_model_comparison(comparison_df: pd.DataFrame,
                         metric: str = 'R² Score',
                         save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot model comparison for a specific metric

    Args:
        comparison_df: DataFrame with model comparison
        metric: Metric to plot
        save_path: Path to save figure

    Returns:
        Figure object
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Sort by metric
    df_sorted = comparison_df.sort_values(metric, ascending=True)

    # Bar plot
    bars = ax.barh(df_sorted['Model'], df_sorted[metric])

    # Color bars
    colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(df_sorted)))
    for bar, color in zip(bars, colors):
        bar.set_color(color)

    # Labels
    ax.set_xlabel(metric, fontsize=12)
    ax.set_title(f'Model Comparison - {metric}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')

    # Add value labels on bars
    for i, (idx, row) in enumerate(df_sorted.iterrows()):
        value = row[metric]
        ax.text(value, i, f' {value:.4f}', va='center', fontsize=10)

    plt.tight_layout()
    _save_figure(fig, save_path)

    return fig


def plot_all_metrics_comparison(comparison_df: pd.DataFrame,
                                save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot comparison of all metrics across models

    Args:
        comparison_df: DataFrame with model comparison
        save_path: Path to save figure

    Returns:
        Figure object
    """
    metrics = ['R² Score', 'RMSE', 'MAE', 'MAPE (%)']
    n_metrics = len(metrics)

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    for idx, metric in enumerate(metrics):
        ax = axes[idx]
        df_sorted = comparison_df.sort_values(metric, ascending=(metric != 'R² Score'))

        bars = ax.barh(df_sorted['Model'], df_sorted[metric])

        # Color based on metric type
        if metric == 'R² Score':
            colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(df_sorted)))
        else:
            colors = plt.cm.RdYlGn_r(np.linspace(0.3, 0.9, len(df_sorted)))

        for bar, color in zip(bars, colors):
            bar.set_color(color)

        ax.set_xlabel(metric, fontsize=11)
        ax.set_title(f'{metric} Comparison', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')

        # Add value labels
        for i, (idx_row, row) in enumerate(df_sorted.iterrows()):
            value = row[metric]
            ax.text(value, i, f' {value:.4f}', va='center', fontsize=9)

    plt.suptitle('Model Performance Comparison - All Metrics', fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    _save_figure(fig, save_path)

    return fig


def create_report_figures(results: Dict[str, Any],
                         comparison_df: pd.DataFrame,
                         save_dir: str):
    """
    Create and save all report figures

    Args:
        results: Dictionary with all model results
        comparison_df: DataFrame with model comparison
        save_dir: Directory to save figures
    """
    Path(save_dir).mkdir(parents=True, exist_ok=True)

    print("Generating report figures...")

    # 1. Model comparison - all metrics
    plot_all_metrics_comparison(
        comparison_df,
        save_path=f"{save_dir}/model_comparison_all_metrics.png"
    )
    plt.close()

    # 2. Individual model plots
    for model_name, result in results.items():
        model_dir = f"{save_dir}/{model_name.lower().replace(' ', '_')}"
        Path(model_dir).mkdir(parents=True, exist_ok=True)

        # Actual vs Predicted
        if 'y_test' in result and 'y_pred' in result:
            plot_actual_vs_predicted(
                result['y_test'],
                result['y_pred'],
                model_name,
                save_path=f"{model_dir}/actual_vs_predicted.png"
            )
            plt.close()

            # Residuals
            plot_residuals(
                result['y_test'],
                result['y_pred'],
                model_name,
                save_path=f"{model_dir}/residuals.png"
            )
            plt.close()

        # Feature importance
        if 'feature_importance' in result and result['feature_importance'] is not None:
            plot_feature_importance(
                result['feature_importance'],
                model_name,
                save_path=f"{model_dir}/feature_importance.png"
            )
            plt.close()

    print(f"All figures saved to {save_dir}")


def plot_prediction_errors(y_true: np.ndarray,
                          y_pred: np.ndarray,
                          model_name: str = "Model",
                          save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot prediction error distribution

    Args:
        y_true: True values
        y_pred: Predicted values
        model_name: Name of the model
        save_path: Path to save figure

    Returns:
        Figure object
    """
    errors = y_true - y_pred
    percentage_errors = (errors / y_true) * 100

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    # Absolute errors
    axes[0].hist(np.abs(errors), bins=50, edgecolor='black', alpha=0.7, color='skyblue')
    axes[0].axvline(x=np.mean(np.abs(errors)), color='r', linestyle='--', lw=2,
                   label=f'Mean: {np.mean(np.abs(errors)):.2f}')
    axes[0].set_xlabel('Absolute Error (billion VND)', fontsize=12)
    axes[0].set_ylabel('Frequency', fontsize=12)
    axes[0].set_title(f'Absolute Error Distribution - {model_name}', fontsize=14, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Percentage errors
    axes[1].hist(np.abs(percentage_errors), bins=50, edgecolor='black', alpha=0.7, color='lightcoral')
    axes[1].axvline(x=np.mean(np.abs(percentage_errors)), color='r', linestyle='--', lw=2,
                   label=f'Mean: {np.mean(np.abs(percentage_errors)):.2f}%')
    axes[1].set_xlabel('Absolute Percentage Error (%)', fontsize=12)
    axes[1].set_ylabel('Frequency', fontsize=12)
    axes[1].set_title(f'Percentage Error Distribution - {model_name}', fontsize=14, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    _save_figure(fig, save_path)

    return fig

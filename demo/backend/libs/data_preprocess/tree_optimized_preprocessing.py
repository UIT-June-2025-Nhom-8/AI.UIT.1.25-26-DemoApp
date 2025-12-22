"""
Tree-Optimized Preprocessing Pipeline for Vietnam Housing Dataset
Optimized specifically for LightGBM and XGBoost models

This pipeline integrates:
- Basic preprocessing from main_preprocessing.py
- Enhanced features from enhanced_preprocessing.py
- Tree-model optimizations (label encoding, no scaling by default)
- Scientific rigor (no data leakage, proper train/test split)

Author: CS106.TTNT Final Project
Date: 2025-12-16
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
from pathlib import Path
import warnings
from typing import Tuple, Dict, Optional

# Import existing functions
from data_preprocessor import DataPreprocessor
from enhanced_preprocessing import (
    remove_outliers_iqr,
    group_rare_categories,
    remove_rare_categories,
    create_interaction_features,
    create_location_features_train,
    create_location_features_test
)

warnings.filterwarnings("ignore")

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DATASET_DIR = PROJECT_ROOT / "dataset"
RAW_DIR = DATASET_DIR / "raw"
PROCESSED_DIR = DATASET_DIR / "processed"

# Ensure directories exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# STEP 1: BASIC PREPROCESSING (Reuse from main_preprocessing.py)
# ==============================================================================

def basic_preprocessing(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Apply basic preprocessing: missing value handling and feature engineering

    Reuses logic from main_preprocessing.py with improvements:
    - Furniture state: group by Price quartile
    - Legal status: group by city

    Args:
        df: Raw dataframe
        verbose: Print progress

    Returns:
        Preprocessed dataframe
    """
    if verbose:
        print("\n" + "=" * 80)
        print("🔧 BASIC PREPROCESSING")
        print("=" * 80)

    prep = DataPreprocessor(df, verbose=verbose)

    # ========================================
    # PHASE 1: Handle HIGH missing (>70%)
    # ========================================
    if verbose:
        print("\n📍 Phase 1: Handle HIGH missing features (>70%)")

    # Balcony direction (82.65% missing)
    if "Balcony direction" in df.columns:
        prep.add_binary_flag("Balcony direction", "new_has_balcony_direction").fill_value(
            "Balcony direction", "Unknown"
        )

    # House direction (70.26% missing)
    if "House direction" in df.columns:
        prep.add_binary_flag("House direction", "new_has_house_direction").fill_value(
            "House direction", "Không rõ"
        )

    # ========================================
    # PHASE 2: Handle MODERATE missing (30-70%)
    # ========================================
    if verbose:
        print("\n📍 Phase 2: Handle MODERATE missing features (30-70%)")

    # Furniture state: Fill by city (urban areas have different patterns)
    if "new_city" not in prep.df.columns and "Address" in prep.df.columns:
        prep.extract_from_address("Address")

    df_copy = prep.df.copy()
    for city in df_copy['new_city'].unique():
        city_mask = df_copy['new_city'] == city
        mode_val = df_copy.loc[city_mask, 'Furniture state'].mode()
        if len(mode_val) > 0:
            missing_mask = city_mask & df_copy['Furniture state'].isna()
            df_copy.loc[missing_mask, 'Furniture state'] = mode_val.iloc[0]

    remaining_missing = df_copy['Furniture state'].isna().sum()
    if remaining_missing > 0:
        global_mode = df_copy['Furniture state'].mode()
        if len(global_mode) > 0:
            df_copy['Furniture state'].fillna(global_mode.iloc[0], inplace=True)

    prep.df['Furniture state'] = df_copy['Furniture state']

    if verbose:
        print(f"   ✅ Filled Furniture state (grouped by city)")

    # Access Road (43.99% missing)
    if "Access Road" in df.columns:
        prep.add_binary_flag("Access Road", "new_has_access_road").fill_value("Access Road", 0)

    # Frontage (38.25% missing)
    if "Frontage" in df.columns:
        prep.add_binary_flag("Frontage", "has_frontage").fill_value("Frontage", 0)

    # ========================================
    # PHASE 3: Handle LOW missing (<30%)
    # ========================================
    if verbose:
        print("\n📍 Phase 3: Handle LOW missing features (<30%)")

    # Bathrooms (grouped by Bedrooms) - EXCELLENT strategy, keep it!
    if "Bathrooms" in df.columns and "Bedrooms" in df.columns:
        if df["Bedrooms"].isna().sum() > 0:
            prep.fill_median("Bedrooms")
        prep.fill_median("Bathrooms", group_by="Bedrooms")
    elif "Bathrooms" in df.columns:
        prep.fill_median("Bathrooms")

    # 🆕 IMPROVEMENT: Legal status - group by city
    # Legal requirements differ by province
    if "Legal status" in df.columns:
        # First extract location if not done
        if "new_city" not in prep.df.columns and "Address" in prep.df.columns:
            prep.extract_from_address("Address")

        # Group-based imputation if new_city exists
        if "new_city" in prep.df.columns:
            df_copy = prep.df.copy()
            for city in df_copy['new_city'].unique():
                mask = df_copy['new_city'] == city
                mode_val = df_copy.loc[mask, 'Legal status'].mode()
                if len(mode_val) > 0:
                    df_copy.loc[mask & df_copy['Legal status'].isna(), 'Legal status'] = mode_val[0]

            # Fill any remaining
            if df_copy['Legal status'].isna().sum() > 0:
                df_copy['Legal status'].fillna("Không rõ", inplace=True)

            prep.df['Legal status'] = df_copy['Legal status']
            if verbose:
                print(f"   ✅ Filled Legal status (grouped by city)")
        else:
            prep.fill_value("Legal status", "Không rõ")

    # Floors
    if "Floors" in df.columns:
        prep.fill_mode("Floors")

    # Fill remaining numeric columns with median
    numeric_cols = prep.df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if prep.df[col].isna().sum() > 0:
            prep.fill_median(col)

    # ========================================
    # PHASE 4: Feature Engineering
    # ========================================
    if verbose:
        print("\n📍 Phase 4: Feature Engineering (Basic)")

    # Room-related features
    if "Bathrooms" in prep.df.columns and "Bedrooms" in prep.df.columns:
        prep.create_feature(
            "new_bathroom_bedroom_ratio",
            lambda df: df["Bathrooms"] / df["Bedrooms"].replace(0, 1),
            "Bathroom to Bedroom ratio"
        )
        prep.create_feature(
            "new_total_rooms",
            lambda df: df["Bedrooms"] + df["Bathrooms"],
            "Total number of rooms"
        )

    # Area-related features
    if "Area" in prep.df.columns:
        prep.create_feature(
            "new_is_large_house",
            lambda df: (df["Area"] > 140).astype(int),
            "Flag for large houses (>140m²)"
        )

        if "new_total_rooms" in prep.df.columns:
            prep.create_feature(
                "new_avg_room_size",
                lambda df: df["Area"] / df["new_total_rooms"].replace(0, 1),
                "Average room size"
            )

    # Luxury and multi-story indicators
    if "Bathrooms" in prep.df.columns:
        prep.create_feature(
            "new_is_luxury",
            lambda df: (df["Bathrooms"] >= 4).astype(int),
            "Luxury house indicator (4+ bathrooms)"
        )

    if "Floors" in prep.df.columns:
        prep.create_feature(
            "new_is_multi_story",
            lambda df: (df["Floors"] > 2).astype(int),
            "Multi-story house indicator"
        )

    # Location extraction
    if "Address" in prep.df.columns and "new_city" not in prep.df.columns:
        prep.extract_from_address("Address")

    # Area categories (useful for some trees)
    if "Area" in prep.df.columns:
        prep.create_bins(
            "Area", n_bins=5, labels=["Rất nhỏ", "Nhỏ", "Trung bình", "Lớn", "Rất lớn"]
        )

    if verbose:
        print(f"\n✅ Basic preprocessing complete!")
        print(f"   Shape: {prep.df.shape}")
        print(f"   New features: {len(prep.new_features)}")

    return prep.df


# ==============================================================================
# STEP 2: ENHANCED PREPROCESSING
# ==============================================================================

def enhanced_preprocessing(df: pd.DataFrame, config: dict, verbose: bool = True) -> pd.DataFrame:
    """
    Apply enhanced preprocessing: outlier removal, interaction features

    Args:
        df: Basic preprocessed dataframe
        config: Configuration dict with outlier_removal, etc.
        verbose: Print progress

    Returns:
        Enhanced dataframe
    """
    if verbose:
        print("\n" + "=" * 80)
        print("🚀 ENHANCED PREPROCESSING")
        print("=" * 80)

    df_enhanced = df.copy()

    # ========================================
    # PHASE 1: Outlier Removal - MOVED to split_and_encode (after split)
    # ========================================
    if verbose:
        print("\n📍 Phase 1: Outlier Removal - SKIPPED (will be done after train/test split)")

    # ========================================
    # PHASE 2: Remove/Group Rare Categories
    # ========================================
    encoding_config = config.get('encoding', {})
    high_card_config = encoding_config.get('high_cardinality', {})
    rare_threshold = high_card_config.get('rare_threshold', 100)

    if verbose:
        print("\n📍 Phase 2: Remove/Group Rare Categories")

    # Remove rare cities (< 10 samples) to clean data quality issues
    if "new_city" in df_enhanced.columns:
        df_enhanced = remove_rare_categories(
            df_enhanced, "new_city", min_count=10
        )

    # Group rare districts and street_ward (too granular to remove)
    if "new_district" in df_enhanced.columns:
        df_enhanced = group_rare_categories(
            df_enhanced, "new_district", min_count=rare_threshold, group_name="Other"
        )

    if "new_street_ward" in df_enhanced.columns:
        df_enhanced = group_rare_categories(
            df_enhanced, "new_street_ward", min_count=rare_threshold, group_name="Other"
        )

    # ========================================
    # PHASE 3: Create Interaction Features
    # ========================================
    feature_config = config.get('feature_engineering', {})
    if feature_config.get('interactions', {}).get('enabled', True):
        if verbose:
            print("\n📍 Phase 3: Create Interaction Features")
        df_enhanced = create_interaction_features(df_enhanced)

    if verbose:
        print(f"\n✅ Enhanced preprocessing complete!")
        print(f"   Shape: {df_enhanced.shape}")

    return df_enhanced


# ==============================================================================
# STEP 3: TRAIN/TEST SPLIT & ENCODING (SCIENTIFIC - NO DATA LEAKAGE)
# ==============================================================================

def split_and_encode(
    df: pd.DataFrame,
    config: dict,
    test_size: float = 0.2,
    random_state: int = 42,
    verbose: bool = True
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
    """
    Split data and apply encoding (FIT on train ONLY)

    SCIENTIFIC METHOD:
    1. Split into train/test FIRST
    2. Create location features (fit on train only)
    3. Label encode categorical (fit on train only)
    4. Optional scaling (fit on train only)

    Args:
        df: Enhanced dataframe
        config: Configuration dict
        test_size: Test set proportion
        random_state: Random seed
        verbose: Print progress

    Returns:
        (train_df, test_df, artifacts) where artifacts contains fitted objects
    """
    if verbose:
        print("\n" + "=" * 80)
        print("🔬 SCIENTIFIC SPLIT & ENCODING (No Data Leakage)")
        print("=" * 80)

    # ========================================
    # PHASE 1: Train/Test Split
    # ========================================
    if verbose:
        print(f"\n📍 Phase 1: Train/Test Split ({int((1-test_size)*100)}%/{int(test_size*100)}%)")

    if "Price" not in df.columns:
        raise ValueError("Price column not found!")

    # Drop Address (redundant with district/city)
    exclude_features = config.get('preprocessing', {}).get('exclude_features', ['Address'])
    df_clean = df.drop(columns=[col for col in exclude_features if col in df.columns], errors='ignore')

    X = df_clean.drop(columns=["Price"])
    y = df_clean["Price"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    if verbose:
        print(f"   ✅ Train: {len(X_train):,} samples")
        print(f"   ✅ Test: {len(X_test):,} samples")

    # ========================================
    # PHASE 1.5: Remove Outliers from TRAIN ONLY
    # ========================================
    outlier_config = config.get('preprocessing', {}).get('outlier_removal', {})
    if outlier_config.get('enabled', True):
        if verbose:
            print("\n📍 Phase 1.5: Outlier Removal (Train Only - Anti-Leakage)")

        method = outlier_config.get('method', 'iqr')
        params = outlier_config.get('params', {}).get(method, {})

        if method == 'iqr':
            multiplier = params.get('multiplier', 1.5)
            Q1 = y_train.quantile(0.25)
            Q3 = y_train.quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - multiplier * IQR
            upper = Q3 + multiplier * IQR
            mask = (y_train >= lower) & (y_train <= upper)
            removed = len(y_train) - mask.sum()

            X_train = X_train[mask]
            y_train = y_train[mask]

            if verbose:
                print(f"   IQR bounds: {lower:.1f} to {upper:.1f}")
                print(f"   ✅ Removed {removed:,} outliers from train ({removed/len(mask)*100:.2f}%)")
                print(f"   ✅ Train: {len(X_train):,} samples (after outlier removal)")
                print(f"   ✅ Test: {len(X_test):,} samples (unchanged)")

    # ========================================
    # PHASE 2: Location-Based Features (FIT on train ONLY)
    # ========================================
    feature_config = config.get('preprocessing', {}).get('feature_engineering', {})
    location_config = feature_config.get('location_features', {})
    location_stats = None

    if location_config.get('enabled', True) and "new_district" in X_train.columns:
        if verbose:
            print("\n📍 Phase 2: Location-Based Aggregated Features (Anti-Leakage)")

        # FIT on train
        X_train, location_stats = create_location_features_train(
            X_train, location_col="new_district"
        )

        # APPLY to test (using train stats)
        X_test = create_location_features_test(
            X_test, location_stats, location_col="new_district"
        )

    # ========================================
    # PHASE 3: Label Encoding (FIT on train ONLY)
    # ========================================
    if verbose:
        print("\n📍 Phase 3: Label Encoding for Categorical Features")

    encoding_config = config.get('preprocessing', {}).get('encoding', {})
    low_card_cols = encoding_config.get('low_cardinality', {}).get('columns', [])
    high_card_cols = encoding_config.get('high_cardinality', {}).get('columns', [])

    # Filter existing columns
    low_card_cols = [col for col in low_card_cols if col in X_train.columns]
    high_card_cols = [col for col in high_card_cols if col in X_train.columns]

    all_cat_cols = low_card_cols + high_card_cols

    label_encoders = {}

    for col in all_cat_cols:
        le = LabelEncoder()

        # Fit on train
        X_train[col] = le.fit_transform(X_train[col].astype(str))
        label_encoders[col] = le

        # Transform test (handle unknowns)
        test_values = X_test[col].astype(str)
        encoded = []
        for val in test_values:
            if val in le.classes_:
                encoded.append(le.transform([val])[0])
            else:
                encoded.append(-1)  # Trees can handle -1 as unknown
        X_test[col] = encoded

    if verbose:
        print(f"   ✅ Label encoded {len(all_cat_cols)} categorical columns")
        print(f"      Low-cardinality: {len(low_card_cols)}")
        print(f"      High-cardinality: {len(high_card_cols)}")

    # ========================================
    # PHASE 4: Optional Scaling (for regularization)
    # ========================================
    scaling_config = config.get('preprocessing', {}).get('scaling', {})
    scaler = None

    if scaling_config.get('scale_interactions', False):
        if verbose:
            print("\n📍 Phase 4: Scaling Interaction Features (for regularization)")

        interaction_cols = scaling_config.get('interaction_columns', [])
        interaction_cols = [col for col in interaction_cols if col in X_train.columns]

        if interaction_cols:
            scaler = StandardScaler()
            X_train[interaction_cols] = scaler.fit_transform(X_train[interaction_cols])
            X_test[interaction_cols] = scaler.transform(X_test[interaction_cols])

            if verbose:
                print(f"   ✅ Scaled {len(interaction_cols)} interaction features")
    elif verbose:
        print("\n📍 Phase 4: Scaling SKIPPED (tree models don't need scaling)")

    # ========================================
    # Combine with target
    # ========================================
    train_df = X_train.copy()
    train_df['Price'] = y_train.values

    test_df = X_test.copy()
    test_df['Price'] = y_test.values

    # ========================================
    # Prepare artifacts
    # ========================================
    artifacts = {
        'label_encoders': label_encoders,
        'location_stats': location_stats,
        'scaler': scaler,
        'feature_columns': X_train.columns.tolist(),
        'config': config
    }

    if verbose:
        print(f"\n✅ Split & encoding complete!")
        print(f"   Train shape: {train_df.shape}")
        print(f"   Test shape: {test_df.shape}")
        print(f"   Total features: {len(X_train.columns)}")

    return train_df, test_df, artifacts


# ==============================================================================
# MAIN PIPELINE
# ==============================================================================

def tree_optimized_pipeline(
    input_file: Optional[str] = None,
    output_train: str = "train_optimized.csv",
    output_test: str = "test_optimized.csv",
    config: Optional[dict] = None,
    test_size: float = 0.2,
    random_state: int = 42,
    verbose: bool = True
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
    """
    Complete tree-optimized preprocessing pipeline

    Pipeline steps:
    1. Load raw data
    2. Basic preprocessing (missing values, basic features)
    3. Enhanced preprocessing (outliers, interactions)
    4. Train/test split
    5. Location features (fit on train only)
    6. Label encoding (fit on train only)
    7. Optional scaling
    8. Save outputs and artifacts

    Args:
        input_file: Path to raw CSV (defaults to vietnam_housing_dataset.csv)
        output_train: Output filename for train set
        output_test: Output filename for test set
        config: Configuration dict (defaults loaded if None)
        test_size: Proportion for test set
        random_state: Random seed for reproducibility
        verbose: Print detailed progress

    Returns:
        (train_df, test_df, artifacts)
    """

    print("\n" + "=" * 80)
    print("🌳 TREE-OPTIMIZED PREPROCESSING PIPELINE")
    print("   Optimized for LightGBM and XGBoost")
    print("=" * 80)

    # Default config if not provided
    if config is None:
        config = {
            'preprocessing': {
                'outlier_removal': {
                    'enabled': True,
                    'method': 'iqr',
                    'target_column': 'Price',
                    'params': {'iqr': {'multiplier': 1.5}}
                },
                'encoding': {
                    'method': 'label',
                    'low_cardinality': {
                        'columns': ['House direction', 'Balcony direction', 'Legal status',
                                  'Furniture state', 'Area_binned', 'new_city']
                    },
                    'high_cardinality': {
                        'columns': ['new_district', 'new_street_ward'],
                        'rare_threshold': 100
                    }
                },
                'scaling': {
                    'enabled': False,
                    'scale_interactions': False
                },
                'feature_engineering': {
                    'interactions': {'enabled': True},
                    'location_features': {'enabled': True}
                },
                'exclude_features': ['Address']
            }
        }

    # Default input file
    if input_file is None:
        input_file = str(RAW_DIR / "vietnam_housing_dataset.csv")

    # ========================================
    # STEP 1: Load Data
    # ========================================
    if verbose:
        print(f"\n📂 Step 1: Loading data from {input_file}")

    df_raw = pd.read_csv(input_file)

    if verbose:
        print(f"   ✅ Loaded {len(df_raw):,} records × {len(df_raw.columns)} columns")

    # ========================================
    # STEP 2: Basic Preprocessing
    # ========================================
    df_basic = basic_preprocessing(df_raw, verbose=verbose)

    # ========================================
    # STEP 3: Enhanced Preprocessing
    # ========================================
    df_enhanced = enhanced_preprocessing(df_basic, config.get('preprocessing', {}), verbose=verbose)

    # ========================================
    # STEP 4: Split & Encode
    # ========================================
    train_df, test_df, artifacts = split_and_encode(
        df_enhanced,
        config,
        test_size=test_size,
        random_state=random_state,
        verbose=verbose
    )

    # ========================================
    # STEP 5: Save Outputs
    # ========================================
    if verbose:
        print("\n" + "=" * 80)
        print("💾 SAVING OUTPUTS")
        print("=" * 80)

    # Save datasets
    train_path = PROCESSED_DIR / output_train
    test_path = PROCESSED_DIR / output_test

    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    if verbose:
        print(f"\n✅ Saved datasets:")
        print(f"   • {train_path} ({train_df.shape})")
        print(f"   • {test_path} ({test_df.shape})")

    # Save artifacts
    if artifacts['label_encoders']:
        encoders_path = PROCESSED_DIR / "encoders_optimized.pkl"
        joblib.dump(artifacts['label_encoders'], encoders_path)
        if verbose:
            print(f"   • {encoders_path.name} ({len(artifacts['label_encoders'])} encoders)")

    if artifacts['location_stats'] is not None:
        location_path = PROCESSED_DIR / "location_stats_optimized.pkl"
        joblib.dump(artifacts['location_stats'], location_path)
        if verbose:
            print(f"   • {location_path.name}")

    if artifacts['scaler'] is not None:
        scaler_path = PROCESSED_DIR / "scaler_optimized.pkl"
        joblib.dump(artifacts['scaler'], scaler_path)
        if verbose:
            print(f"   • {scaler_path.name}")

    # Save processing report
    report_path = PROCESSED_DIR / "preprocessing_report_optimized.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("TREE-OPTIMIZED PREPROCESSING REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Input file: {input_file}\n")
        f.write(f"Raw data shape: {df_raw.shape}\n")
        f.write(f"After basic preprocessing: {df_basic.shape}\n")
        f.write(f"After enhanced preprocessing: {df_enhanced.shape}\n")
        f.write(f"Train set: {train_df.shape}\n")
        f.write(f"Test set: {test_df.shape}\n\n")

        f.write(f"Rows removed (outliers): {len(df_basic) - len(df_enhanced):,} ")
        f.write(f"({(len(df_basic) - len(df_enhanced))/len(df_basic)*100:.2f}%)\n\n")

        f.write(f"Total features: {len(train_df.columns) - 1}\n")
        f.write(f"Categorical encoded: {len(artifacts['label_encoders'])}\n")
        f.write(f"Location stats fitted: {'Yes' if artifacts['location_stats'] is not None else 'No'}\n")
        f.write(f"Scaling applied: {'Yes' if artifacts['scaler'] is not None else 'No'}\n\n")

        f.write("Configuration:\n")
        f.write(f"{config}\n")

    if verbose:
        print(f"   • {report_path.name}")

    # ========================================
    # FINAL SUMMARY
    # ========================================
    if verbose:
        print("\n" + "=" * 80)
        print("✅ PIPELINE COMPLETE!")
        print("=" * 80)
        print(f"\n📊 Summary:")
        print(f"   • Original: {len(df_raw):,} records × {len(df_raw.columns)} features")
        print(f"   • After outlier removal: {len(df_enhanced):,} records ({(len(df_raw)-len(df_enhanced))/len(df_raw)*100:.1f}% removed)")
        print(f"   • Final features: {len(train_df.columns) - 1}")
        print(f"   • Train set: {len(train_df):,} records")
        print(f"   • Test set: {len(test_df):,} records")
        print(f"\n🎯 Ready for LightGBM and XGBoost training!")

    return train_df, test_df, artifacts


# ==============================================================================
# VALIDATION FUNCTIONS
# ==============================================================================

def validate_preprocessed_data(train_df: pd.DataFrame, test_df: pd.DataFrame) -> bool:
    """
    Validate preprocessed data for common issues

    Args:
        train_df: Training dataframe
        test_df: Test dataframe

    Returns:
        True if all checks pass, False otherwise
    """
    print("\n" + "=" * 80)
    print("✅ DATA VALIDATION CHECKS")
    print("=" * 80)

    checks = []

    # 1. No missing values
    train_missing = train_df.isnull().sum().sum()
    test_missing = test_df.isnull().sum().sum()
    passed = (train_missing == 0 and test_missing == 0)
    checks.append(("No missing values", passed))
    if not passed:
        print(f"   ❌ Missing values: Train={train_missing}, Test={test_missing}")

    # 2. Same columns
    passed = set(train_df.columns) == set(test_df.columns)
    checks.append(("Same columns in train/test", passed))
    if not passed:
        train_only = set(train_df.columns) - set(test_df.columns)
        test_only = set(test_df.columns) - set(train_df.columns)
        print(f"   ❌ Train-only columns: {train_only}")
        print(f"   ❌ Test-only columns: {test_only}")

    # 3. Price in both
    passed = ('Price' in train_df.columns and 'Price' in test_df.columns)
    checks.append(("Price column present", passed))

    # 4. Feature count reasonable
    n_features = len(train_df.columns) - 1
    passed = (40 <= n_features <= 70)
    checks.append((f"Feature count in range (40-70): {n_features}", passed))

    # 5. No infinite values
    train_inf = np.isinf(train_df.select_dtypes(include=[np.number])).sum().sum()
    test_inf = np.isinf(test_df.select_dtypes(include=[np.number])).sum().sum()
    passed = (train_inf == 0 and test_inf == 0)
    checks.append(("No infinite values", passed))

    # 6. Similar target distribution
    if 'Price' in train_df.columns and 'Price' in test_df.columns:
        train_mean = train_df['Price'].mean()
        test_mean = test_df['Price'].mean()
        diff_pct = abs(train_mean - test_mean) / train_mean * 100
        passed = (diff_pct < 10)
        checks.append((f"Similar Price distribution (diff={diff_pct:.1f}%)", passed))

    # 7. All features numeric
    train_non_numeric = train_df.select_dtypes(exclude=[np.number]).columns.tolist()
    test_non_numeric = test_df.select_dtypes(exclude=[np.number]).columns.tolist()
    # Remove Price if it's in the list
    train_non_numeric = [col for col in train_non_numeric if col != 'Price']
    test_non_numeric = [col for col in test_non_numeric if col != 'Price']
    passed = (len(train_non_numeric) == 0 and len(test_non_numeric) == 0)
    checks.append(("All features numeric", passed))
    if not passed:
        print(f"   ❌ Non-numeric in train: {train_non_numeric}")
        print(f"   ❌ Non-numeric in test: {test_non_numeric}")

    # Print results
    print()
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")

    all_passed = all(passed for _, passed in checks)

    if all_passed:
        print("\n🎉 All validation checks PASSED!")
    else:
        print("\n⚠️ Some validation checks FAILED. Please review.")

    return all_passed


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    print("\n" + "🌳" * 40)
    print("TREE-OPTIMIZED PREPROCESSING PIPELINE FOR VIETNAM HOUSING")
    print("🌳" * 40)

    # Run pipeline
    train_df, test_df, artifacts = tree_optimized_pipeline(
        verbose=True
    )

    # Validate
    validate_preprocessed_data(train_df, test_df)

    print("\n" + "=" * 80)
    print("🎯 NEXT STEPS:")
    print("=" * 80)
    print("1. Load data: train = pd.read_csv('dataset/processed/train_optimized.csv')")
    print("2. Update model_config.yaml to use train_optimized.csv and test_optimized.csv")
    print("3. Train LightGBM and XGBoost models")
    print("4. Compare performance with old pipeline (train_final.csv)")
    print("5. Analyze feature importances to identify features for exclude_features")
    print("\n✨ Happy modeling!")

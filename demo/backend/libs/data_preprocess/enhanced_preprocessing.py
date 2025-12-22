"""
Enhanced Preprocessing Pipeline for Vietnam Housing Dataset
Implements advanced feature engineering and data cleaning techniques

Author: CS106.TTNT Final Project
Date: 2025-12-16
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import mutual_info_regression
from sklearn.ensemble import RandomForestRegressor
import warnings

warnings.filterwarnings("ignore")


# ============================================================================
# 1. OUTLIER REMOVAL
# ============================================================================


def remove_outliers_iqr(
    df: pd.DataFrame, column: str = "Price", multiplier: float = 1.5
) -> pd.DataFrame:
    """
    Remove outliers using IQR method (on ORIGINAL scale, before log transform)

    Args:
        df: Input dataframe
        column: Column to check for outliers
        multiplier: IQR multiplier (1.5 = standard, 3.0 = extreme only)

    Returns:
        Dataframe with outliers removed
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1

    lower = Q1 - multiplier * IQR
    upper = Q3 + multiplier * IQR

    mask = (df[column] >= lower) & (df[column] <= upper)
    removed = len(df) - mask.sum()

    print(f"📍 Outlier Removal (IQR method):")
    print(f"   Lower bound: {lower:,.0f}")
    print(f"   Upper bound: {upper:,.0f}")
    print(f"   Removed: {removed:,} samples ({removed/len(df)*100:.2f}%)")

    return df[mask].reset_index(drop=True)


def remove_outliers_percentile(
    df: pd.DataFrame, column: str = "Price", lower: float = 1, upper: float = 99
) -> pd.DataFrame:
    """
    Remove outliers using percentile method

    Args:
        df: Input dataframe
        column: Column to check for outliers
        lower: Lower percentile (e.g., 1 for 1st percentile)
        upper: Upper percentile (e.g., 99 for 99th percentile)

    Returns:
        Dataframe with outliers removed
    """
    lower_val = df[column].quantile(lower / 100)
    upper_val = df[column].quantile(upper / 100)

    mask = (df[column] >= lower_val) & (df[column] <= upper_val)
    removed = len(df) - mask.sum()

    print(f"📍 Outlier Removal (Percentile method: {lower}%-{upper}%):")
    print(f"   Lower threshold: {lower_val:,.0f}")
    print(f"   Upper threshold: {upper_val:,.0f}")
    print(f"   Removed: {removed:,} samples ({removed/len(df)*100:.2f}%)")

    return df[mask].reset_index(drop=True)


def remove_outliers_zscore(
    df: pd.DataFrame, column: str = "Price", threshold: float = 3.0
) -> pd.DataFrame:
    """
    Remove outliers using Z-score method

    Args:
        df: Input dataframe
        column: Column to check for outliers
        threshold: Z-score threshold (3.0 = 99.7% data retained)

    Returns:
        Dataframe with outliers removed
    """
    mean = df[column].mean()
    std = df[column].std()
    z_scores = np.abs((df[column] - mean) / std)

    mask = z_scores < threshold
    removed = len(df) - mask.sum()

    print(f"📍 Outlier Removal (Z-score method, threshold={threshold}):")
    print(f"   Mean: {mean:,.0f}")
    print(f"   Std: {std:,.0f}")
    print(f"   Removed: {removed:,} samples ({removed/len(df)*100:.2f}%)")

    return df[mask].reset_index(drop=True)


# ============================================================================
# 2. RARE CATEGORY GROUPING
# ============================================================================


def group_rare_categories(
    df: pd.DataFrame, column: str, min_count: int = 50, group_name: str = "Other"
) -> pd.DataFrame:
    """
    Group rare categories (< min_count samples) into single category

    Args:
        df: Input dataframe
        column: Column to process
        min_count: Minimum samples to keep category separate
        group_name: Name for grouped rare categories

    Returns:
        Dataframe with rare categories grouped
    """
    if column not in df.columns:
        print(f"⚠️ Column '{column}' not found, skipping...")
        return df

    value_counts = df[column].value_counts()
    rare_categories = value_counts[value_counts < min_count].index

    df[column] = df[column].apply(lambda x: group_name if x in rare_categories else x)

    print(f"📍 Grouped rare categories in '{column}':")
    print(f"   Rare categories (< {min_count} samples): {len(rare_categories)}")
    print(f"   Remaining unique values: {df[column].nunique()}")
    print(f"   Samples in '{group_name}': {(df[column] == group_name).sum():,}")

    return df


def remove_rare_categories(
    df: pd.DataFrame, column: str, min_count: int = 10
) -> pd.DataFrame:
    """
    Remove rows with rare categories (< min_count samples)

    Recommended for cleaning data quality issues and removing statistically
    insignificant categories that can cause overfitting.

    Args:
        df: Input dataframe
        column: Column to process
        min_count: Minimum samples to keep the category (default: 10)
                  Recommended values:
                  - 5: Conservative (removes ~0.14% samples)
                  - 10: Balanced (removes ~0.38% samples) ⭐ RECOMMENDED
                  - 20: Aggressive (removes ~0.68% samples)

    Returns:
        Dataframe with rare category rows removed
    """
    if column not in df.columns:
        print(f"⚠️ Column '{column}' not found, skipping...")
        return df

    original_len = len(df)
    value_counts = df[column].value_counts()
    rare_categories = value_counts[value_counts < min_count].index

    # Keep only rows with non-rare categories
    df_filtered = df[~df[column].isin(rare_categories)].copy()

    removed_count = original_len - len(df_filtered)

    print(f"📍 Removed rare categories from '{column}':")
    print(f"   Threshold: < {min_count} samples")
    print(f"   Rare categories removed: {len(rare_categories)}")
    print(f"   Rows removed: {removed_count:,} ({removed_count/original_len*100:.2f}%)")
    print(f"   Remaining rows: {len(df_filtered):,}")
    print(f"   Remaining unique values: {df_filtered[column].nunique()}")

    return df_filtered


# ============================================================================
# 3. INTERACTION FEATURES
# ============================================================================


def create_interaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create multiplicative interaction features

    CRITICAL for improving Area correlation with Price!

    Args:
        df: Input dataframe

    Returns:
        Dataframe with interaction features added
    """
    print("\n📍 Creating Interaction Features:")

    # 1. Area-based interactions (MOST IMPORTANT!)
    if "Area" in df.columns:
        if "Bathrooms" in df.columns:
            df["area_x_bathrooms"] = df["Area"] * df["Bathrooms"]
            print("   ✅ area_x_bathrooms")

        if "Bedrooms" in df.columns:
            df["area_x_bedrooms"] = df["Area"] * df["Bedrooms"]
            print("   ✅ area_x_bedrooms")

        if "Floors" in df.columns:
            df["area_x_floors"] = df["Area"] * df["Floors"]
            print("   ✅ area_x_floors")

    # 2. Room interactions
    if "Bedrooms" in df.columns and "Bathrooms" in df.columns:
        df["bedrooms_x_bathrooms"] = df["Bedrooms"] * df["Bathrooms"]
        print("   ✅ bedrooms_x_bathrooms")

    if "Bedrooms" in df.columns and "Floors" in df.columns:
        df["bedrooms_x_floors"] = df["Bedrooms"] * df["Floors"]
        print("   ✅ bedrooms_x_floors")

    # 3. Luxury score (composite feature)
    if all(col in df.columns for col in ["Bathrooms", "Bedrooms", "Floors", "Area"]):
        df["luxury_score"] = (
            (df["Bathrooms"] >= 4).astype(int)
            + (df["Bedrooms"] >= 5).astype(int)
            + (df["Floors"] >= 4).astype(int)
            + (df["Area"] > 140).astype(int)
        )
        print("   ✅ luxury_score (composite)")

    # 4. Area interactions with major cities (if exists)
    if "new_city" in df.columns and "Area" in df.columns:
        for city in ["Hồ Chí Minh", "Hà Nội", "Bình Dương", "Đà Nẵng"]:
            col_name = f"area_in_{city.replace(' ', '_').lower()}"
            df[col_name] = df["Area"] * (df["new_city"] == city).astype(int)
            if (df["new_city"] == city).sum() > 0:
                print(f"   ✅ {col_name}")

    # 5. Price density (rooms per area)
    if "Area" in df.columns and "new_total_rooms" in df.columns:
        df["room_density"] = df["new_total_rooms"] / df["Area"].replace(0, 1)
        print("   ✅ room_density")

    # 6. Access quality score
    if "Access Road" in df.columns and "Frontage" in df.columns:
        df["access_quality"] = (
            (df["Access Road"] > 0).astype(int) + (df["Frontage"] > 0).astype(int)
        )
        print("   ✅ access_quality")

    print(f"   Total interaction features created: {df.shape[1] - df.shape[1] + 10}")

    return df


# ============================================================================
# 4. LOCATION-BASED FEATURES (Train-only fitting)
# ============================================================================


def create_location_features_train(
    df_train: pd.DataFrame, location_col: str = "new_district"
) -> tuple:
    """
    Create location-based aggregated features (FIT on train set only!)

    Args:
        df_train: Training dataframe (must include 'Price' column)
        location_col: Column name for location grouping

    Returns:
        (df_train_enhanced, location_stats) where location_stats can be used for test set
    """
    if location_col not in df_train.columns:
        print(f"⚠️ Column '{location_col}' not found")
        return df_train, None

    print(f"\n📍 Creating location features from '{location_col}' (TRAIN SET):")

    # Calculate statistics on TRAINING SET ONLY
    # We'll use count-based features (no price-based to avoid leakage)

    location_stats = df_train.groupby(location_col).agg(
        {
            "Area": ["mean", "median", "std"],
            location_col: "count",  # Sample count
        }
    )

    location_stats.columns = [
        f"{location_col}_area_mean",
        f"{location_col}_area_median",
        f"{location_col}_area_std",
        f"{location_col}_sample_count",
    ]

    # Merge back to train
    df_train_enhanced = df_train.merge(
        location_stats, left_on=location_col, right_index=True, how="left"
    )

    # Create tier based on sample count (as numeric for tree models)
    df_train_enhanced[f"{location_col}_tier"] = pd.cut(
        df_train_enhanced[f"{location_col}_sample_count"],
        bins=[0, 50, 200, 500, 10000],
        labels=[0, 1, 2, 3],  # Numeric labels for tree models
    ).astype(int)

    print(f"   ✅ {location_col}_area_mean")
    print(f"   ✅ {location_col}_area_median")
    print(f"   ✅ {location_col}_area_std")
    print(f"   ✅ {location_col}_sample_count")
    print(f"   ✅ {location_col}_tier")

    return df_train_enhanced, location_stats


def create_location_features_test(
    df_test: pd.DataFrame, location_stats: pd.DataFrame, location_col: str = "new_district"
) -> pd.DataFrame:
    """
    Apply location features to TEST set using stats from TRAIN set

    Args:
        df_test: Test dataframe
        location_stats: Statistics calculated from training set
        location_col: Column name for location grouping

    Returns:
        df_test_enhanced with location features added
    """
    if location_stats is None:
        return df_test

    print(f"\n📍 Applying location features to TEST set:")

    # Merge with train statistics
    df_test_enhanced = df_test.merge(
        location_stats, left_on=location_col, right_index=True, how="left"
    )

    # Fill missing (unknown locations in test) with global means
    for col in location_stats.columns:
        if df_test_enhanced[col].isna().sum() > 0:
            global_mean = location_stats[col].mean()
            df_test_enhanced[col].fillna(global_mean, inplace=True)
            print(f"   ⚠️ Filled {df_test_enhanced[col].isna().sum()} missing in {col}")

    # Create tier (as numeric for tree models)
    df_test_enhanced[f"{location_col}_tier"] = pd.cut(
        df_test_enhanced[f"{location_col}_sample_count"],
        bins=[0, 50, 200, 500, 10000],
        labels=[0, 1, 2, 3],  # Numeric labels: 0=Rare, 1=Small, 2=Medium, 3=Large
    ).astype(int)

    print(f"   ✅ Applied {len(location_stats.columns)} location features")

    return df_test_enhanced


# ============================================================================
# 5. FEATURE SELECTION
# ============================================================================


def select_features_correlation(
    X: pd.DataFrame, y: pd.Series, threshold: float = 0.05, k: int = None
) -> list:
    """
    Select features based on correlation with target

    Args:
        X: Feature dataframe
        y: Target series
        threshold: Minimum absolute correlation to keep
        k: If specified, return top k features (overrides threshold)

    Returns:
        List of selected feature names
    """
    # Calculate correlations
    numeric_X = X.select_dtypes(include=[np.number])
    correlations = numeric_X.corrwith(y).abs().sort_values(ascending=False)

    if k is not None:
        selected = correlations.head(k).index.tolist()
        print(f"📍 Correlation-based selection: Top {k} features")
    else:
        selected = correlations[correlations >= threshold].index.tolist()
        print(
            f"📍 Correlation-based selection: {len(selected)} features (threshold={threshold})"
        )

    return selected


def select_features_mutual_info(
    X: pd.DataFrame, y: pd.Series, k: int = 30, random_state: int = 42
) -> list:
    """
    Select features based on mutual information

    Args:
        X: Feature dataframe
        y: Target series
        k: Number of top features to select
        random_state: Random seed

    Returns:
        List of selected feature names
    """
    numeric_X = X.select_dtypes(include=[np.number])

    mi_scores = mutual_info_regression(numeric_X, y, random_state=random_state)
    mi_df = pd.DataFrame({"feature": numeric_X.columns, "mi": mi_scores})
    top_features = mi_df.nlargest(k, "mi")["feature"].tolist()

    print(f"📍 Mutual Information selection: Top {k} features")

    return top_features


def select_features_importance(
    X: pd.DataFrame,
    y: pd.Series,
    k: int = 30,
    n_estimators: int = 100,
    random_state: int = 42,
) -> list:
    """
    Select features based on Random Forest feature importance

    Args:
        X: Feature dataframe
        y: Target series
        k: Number of top features to select
        n_estimators: Number of trees in Random Forest
        random_state: Random seed

    Returns:
        List of selected feature names
    """
    numeric_X = X.select_dtypes(include=[np.number])

    print(f"   Training Random Forest with {n_estimators} trees...")
    rf = RandomForestRegressor(
        n_estimators=n_estimators, random_state=random_state, n_jobs=-1, max_depth=10
    )
    rf.fit(numeric_X, y)

    importance_df = pd.DataFrame(
        {"feature": numeric_X.columns, "importance": rf.feature_importances_}
    )
    top_features = importance_df.nlargest(k, "importance")["feature"].tolist()

    print(f"📍 Random Forest importance selection: Top {k} features")

    return top_features


def select_features_ensemble(
    X: pd.DataFrame,
    y: pd.Series,
    k: int = 40,
    min_votes: int = 2,
    random_state: int = 42,
) -> list:
    """
    Ensemble feature selection: combine multiple methods

    Args:
        X: Feature dataframe
        y: Target series
        k: Number of features to consider from each method
        min_votes: Minimum methods that must select a feature
        random_state: Random seed

    Returns:
        List of selected feature names
    """
    print("\n📍 Ensemble Feature Selection:")
    print(f"   Using {min_votes} voting threshold from 3 methods\n")

    # Method 1: Correlation
    corr_features = select_features_correlation(X, y, k=k)

    # Method 2: Mutual Information
    mi_features = select_features_mutual_info(X, y, k=k, random_state=random_state)

    # Method 3: Random Forest Importance
    rf_features = select_features_importance(
        X, y, k=k, n_estimators=100, random_state=random_state
    )

    # Vote counting
    from collections import Counter

    all_features = corr_features + mi_features + rf_features
    feature_votes = Counter(all_features)

    # Select features with at least min_votes
    selected = [f for f, votes in feature_votes.items() if votes >= min_votes]

    print(f"\n   ✅ Selected {len(selected)} features (≥{min_votes} votes)")
    print(f"   Feature vote distribution:")
    for votes in [3, 2, 1]:
        count = sum(1 for v in feature_votes.values() if v == votes)
        print(f"      {votes} votes: {count} features")

    return selected


# ============================================================================
# 6. DROP LOW-VALUE COLUMNS
# ============================================================================


def drop_high_missing_columns(
    df: pd.DataFrame, threshold: float = 0.7, verbose: bool = True
) -> pd.DataFrame:
    """
    Drop columns that were originally >threshold% missing

    Based on analysis:
    - Balcony direction: 82.65% missing
    - House direction: 70.26% missing

    Args:
        df: Input dataframe
        threshold: Missing percentage threshold (0.7 = 70%)
        verbose: Print dropped columns

    Returns:
        Dataframe with high-missing columns dropped
    """
    columns_to_drop = [
        "Balcony direction",
        "House direction",
        "new_has_balcony_direction",
        "new_has_house_direction",
    ]

    existing_cols = [col for col in columns_to_drop if col in df.columns]

    if verbose and existing_cols:
        print(f"📍 Dropping {len(existing_cols)} high-missing columns:")
        for col in existing_cols:
            print(f"   ❌ {col}")

    return df.drop(columns=existing_cols, errors="ignore")


def drop_low_correlation_columns(
    df: pd.DataFrame, target: str = "Price", threshold: float = 0.03, verbose: bool = True
) -> pd.DataFrame:
    """
    Drop columns with very low correlation to target

    Args:
        df: Input dataframe
        target: Target column name
        threshold: Minimum absolute correlation to keep
        verbose: Print dropped columns

    Returns:
        Dataframe with low-correlation columns dropped
    """
    if target not in df.columns:
        print(f"⚠️ Target '{target}' not found, skipping correlation filter")
        return df

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    correlations = df[numeric_cols].corrwith(df[target]).abs()

    low_corr_cols = correlations[
        (correlations < threshold) & (correlations.index != target)
    ].index.tolist()

    if verbose and low_corr_cols:
        print(
            f"📍 Dropping {len(low_corr_cols)} low-correlation columns (< {threshold}):"
        )
        for col in low_corr_cols:
            corr = correlations[col]
            print(f"   ❌ {col} (corr={corr:.4f})")

    return df.drop(columns=low_corr_cols, errors="ignore")


# ============================================================================
# 7. MAIN ENHANCED PREPROCESSING PIPELINE
# ============================================================================


def enhanced_preprocessing_pipeline(
    df: pd.DataFrame,
    target_col: str = "Price",
    outlier_method: str = "percentile",
    outlier_params: dict = None,
    group_rare_districts: bool = True,
    district_min_count: int = 100,
    create_interactions: bool = True,
    drop_high_missing: bool = True,
    drop_low_corr: bool = True,
    low_corr_threshold: float = 0.03,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Complete enhanced preprocessing pipeline

    Args:
        df: Input dataframe
        target_col: Target column name
        outlier_method: 'percentile', 'iqr', 'zscore', or None
        outlier_params: Parameters for outlier removal
        group_rare_districts: Whether to group rare districts
        district_min_count: Minimum samples for district to remain separate
        create_interactions: Whether to create interaction features
        drop_high_missing: Whether to drop columns with >70% original missing
        drop_low_corr: Whether to drop low-correlation columns
        low_corr_threshold: Correlation threshold for dropping
        verbose: Print progress

    Returns:
        Enhanced dataframe
    """
    if verbose:
        print("\n" + "=" * 80)
        print("🚀 ENHANCED PREPROCESSING PIPELINE")
        print("=" * 80)

    df_enhanced = df.copy()
    original_shape = df_enhanced.shape

    # Step 1: Remove outliers (BEFORE any other processing!)
    if outlier_method:
        if verbose:
            print(f"\n📍 Step 1: Outlier Removal (method={outlier_method})")

        if outlier_params is None:
            outlier_params = {}

        if outlier_method == "percentile":
            df_enhanced = remove_outliers_percentile(
                df_enhanced, column=target_col, **outlier_params
            )
        elif outlier_method == "iqr":
            df_enhanced = remove_outliers_iqr(
                df_enhanced, column=target_col, **outlier_params
            )
        elif outlier_method == "zscore":
            df_enhanced = remove_outliers_zscore(
                df_enhanced, column=target_col, **outlier_params
            )

    # Step 2: Drop high-missing columns
    if drop_high_missing:
        if verbose:
            print(f"\n📍 Step 2: Drop High-Missing Columns")
        df_enhanced = drop_high_missing_columns(df_enhanced, verbose=verbose)

    # Step 3: Group rare categories
    if group_rare_districts:
        if verbose:
            print(f"\n📍 Step 3: Group Rare Categories")

        if "new_district" in df_enhanced.columns:
            df_enhanced = group_rare_categories(
                df_enhanced, "new_district", min_count=district_min_count
            )

        if "new_street_ward" in df_enhanced.columns:
            df_enhanced = group_rare_categories(
                df_enhanced, "new_street_ward", min_count=200
            )

    # Step 4: Create interaction features
    if create_interactions:
        if verbose:
            print(f"\n📍 Step 4: Create Interaction Features")
        df_enhanced = create_interaction_features(df_enhanced)

    # Step 5: Drop low-correlation columns (do this AFTER creating interactions!)
    if drop_low_corr and target_col in df_enhanced.columns:
        if verbose:
            print(f"\n📍 Step 5: Drop Low-Correlation Features")
        df_enhanced = drop_low_correlation_columns(
            df_enhanced, target=target_col, threshold=low_corr_threshold, verbose=verbose
        )

    # Summary
    if verbose:
        print("\n" + "=" * 80)
        print("✅ ENHANCED PREPROCESSING COMPLETE")
        print("=" * 80)
        print(f"   Original shape: {original_shape}")
        print(f"   Final shape: {df_enhanced.shape}")
        print(
            f"   Rows removed: {original_shape[0] - df_enhanced.shape[0]:,} ({(original_shape[0] - df_enhanced.shape[0])/original_shape[0]*100:.2f}%)"
        )
        print(
            f"   Columns removed: {original_shape[1] - df_enhanced.shape[1]} columns"
        )
        print(f"   Columns added: {max(0, df_enhanced.shape[1] - original_shape[1])}")

    return df_enhanced


# ============================================================================
# 8. UTILITY FUNCTIONS
# ============================================================================


def print_feature_correlations(df: pd.DataFrame, target: str = "Price", top_k: int = 20):
    """Print top features by correlation with target"""
    if target not in df.columns:
        print(f"⚠️ Target '{target}' not found")
        return

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    correlations = df[numeric_cols].corrwith(df[target]).abs().sort_values(ascending=False)

    print(f"\n📊 Top {top_k} Features by Correlation with {target}:")
    print("-" * 60)
    for i, (feat, corr) in enumerate(correlations.head(top_k).items(), 1):
        if feat != target:
            bar = "█" * int(corr * 50)
            print(f"{i:2d}. {feat:30s} {corr:.4f} {bar}")


def compare_correlations(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    target: str = "Price",
    top_k: int = 15,
):
    """Compare feature correlations before and after enhancement"""

    print("\n" + "=" * 80)
    print("📊 CORRELATION COMPARISON: Before → After Enhancement")
    print("=" * 80)

    # Get common numeric features
    common_features = list(
        set(df_before.select_dtypes(include=[np.number]).columns)
        & set(df_after.select_dtypes(include=[np.number]).columns)
    )

    if target in common_features:
        common_features.remove(target)

    corr_before = df_before[common_features + [target]].corrwith(df_before[target]).abs()
    corr_after = df_after[common_features + [target]].corrwith(df_after[target]).abs()

    comparison = pd.DataFrame(
        {"Before": corr_before, "After": corr_after, "Improvement": corr_after - corr_before}
    )

    comparison = comparison.sort_values("After", ascending=False).head(top_k)

    print(f"\n{'Feature':<30} {'Before':>10} {'After':>10} {'Change':>10}")
    print("-" * 65)
    for feat, row in comparison.iterrows():
        if feat != target:
            change_symbol = "↑" if row["Improvement"] > 0 else "↓" if row["Improvement"] < 0 else "="
            print(
                f"{feat:<30} {row['Before']:>10.4f} {row['After']:>10.4f} {change_symbol} {abs(row['Improvement']):>8.4f}"
            )

    # Show new features in df_after
    new_features = set(df_after.columns) - set(df_before.columns)
    if new_features and target in df_after.columns:
        print(f"\n\n🆕 NEW FEATURES ({len(new_features)}):")
        print("-" * 65)
        new_corr = df_after[list(new_features) + [target]].corrwith(df_after[target]).abs()
        new_corr = new_corr.sort_values(ascending=False).head(10)
        for feat, corr in new_corr.items():
            if feat != target:
                print(f"{feat:<30} {corr:>10.4f}")

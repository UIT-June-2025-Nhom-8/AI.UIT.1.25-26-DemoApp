# main_preprocessing.py
# Main preprocessing pipeline for Vietnam Housing Dataset
# Uses the generic DataPreprocessor class

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
from data_preprocessor import DataPreprocessor  # Import directly (same folder)
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

warnings.filterwarnings("ignore")

# Get project root directory (2 levels up from this file)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DATASET_DIR = PROJECT_ROOT / "dataset" / "processed"

# Ensure dataset directory exists
DATASET_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.family"] = "Arial"
plt.rcParams["axes.unicode_minus"] = False


def analyze_missing_values(df: pd.DataFrame) -> None:
    """
    Analyze and display missing values in the dataset
    """
    print("\n" + "=" * 80)
    print("📊 MISSING VALUES ANALYSIS")
    print("=" * 80)

    missing_df = pd.DataFrame(
        {
            "Column": df.columns,
            "Missing_Count": df.isnull().sum(),
            "Missing_Percentage": (df.isnull().sum() / len(df) * 100).round(2),
            "Data_Type": df.dtypes,
        }
    )

    missing_df = missing_df[missing_df["Missing_Count"] > 0].sort_values(
        "Missing_Percentage", ascending=False
    )

    if len(missing_df) > 0:
        print("\n📈 Columns with missing values:")
        print(missing_df.to_string(index=False))

        # Categorize by missing percentage
        high_missing = missing_df[missing_df["Missing_Percentage"] > 70]
        moderate_missing = missing_df[
            (missing_df["Missing_Percentage"] > 30)
            & (missing_df["Missing_Percentage"] <= 70)
        ]
        low_missing = missing_df[missing_df["Missing_Percentage"] <= 30]

        if len(high_missing) > 0:
            print(
                f"\n🔴 HIGH missing (>70%): {', '.join(high_missing['Column'].tolist())}"
            )
        if len(moderate_missing) > 0:
            print(
                f"🟡 MODERATE missing (30-70%): {', '.join(moderate_missing['Column'].tolist())}"
            )
        if len(low_missing) > 0:
            print(f"🟢 LOW missing (<30%): {', '.join(low_missing['Column'].tolist())}")
    else:
        print("✅ No missing values found!")


def preprocess_vietnam_housing(
    input_file: str = "../../dataset/raw/vietnam_housing_dataset.csv",
    output_file: str = "../../dataset/processed/vietnam_housing_processed.csv",
) -> pd.DataFrame:
    """
    Main preprocessing pipeline for Vietnam Housing Dataset

    Args:
        input_file: Input CSV filename
        output_file: Output CSV filename

    Returns:
        Processed dataframe
    """

    print("=" * 80)
    print("🏠 VIETNAM HOUSING DATASET - PREPROCESSING PIPELINE")
    print("=" * 80)

    # ========================================
    # STEP 1: LOAD DATA
    # ========================================
    print("\n📂 Step 1: Loading data...")
    df = pd.read_csv(input_file)
    print(f"   ✅ Loaded {len(df):,} records with {len(df.columns)} columns")
    print(f"   Columns: {', '.join(df.columns.tolist())}")

    # ========================================
    # STEP 2: INITIAL ANALYSIS
    # ========================================
    print("\n🔍 Step 2: Initial Analysis")
    analyze_missing_values(df)

    # ========================================
    # STEP 3: INITIALIZE PREPROCESSOR
    # ========================================
    print("\n🔧 Step 3: Starting Preprocessing Pipeline")
    print("-" * 80)

    prep = DataPreprocessor(df, verbose=True)

    # ========================================
    # STEP 4: HANDLE HIGH MISSING (>70%)
    # ========================================
    print("\n📍 Phase 1: Handle HIGH missing features (>70%)")
    print("-" * 60)

    # Balcony direction (82.65% missing)
    if (
        "Balcony direction" in df.columns
        and df["Balcony direction"].isna().sum() / len(df) > 0.7
    ):
        prep.add_binary_flag(
            "Balcony direction", "new_has_balcony_direction"
        ).fill_value("Balcony direction", "Unknown")

    # House direction (70.26% missing)
    if (
        "House direction" in df.columns
        and df["House direction"].isna().sum() / len(df) > 0.7
    ):
        prep.add_binary_flag("House direction", "new_has_house_direction").fill_value(
            "House direction", "Không rõ"
        )

    # ========================================
    # STEP 5: HANDLE MODERATE MISSING (30-70%)
    # ========================================
    print("\n📍 Phase 2: Handle MODERATE missing features (30-70%)")
    print("-" * 60)

    # Furniture state (46.71% missing)
    if "Furniture state" in df.columns:
        prep.fill_value("Furniture state", "Không rõ")

    # Access Road (43.99% missing)
    if "Access Road" in df.columns:
        prep.add_binary_flag("Access Road", "new_has_access_road").fill_value(
            "Access Road", 0
        )

    # Frontage (38.25% missing)
    if "Frontage" in df.columns:
        prep.add_binary_flag("Frontage", "has_frontage").fill_value("Frontage", 0)

    # ========================================
    # STEP 6: HANDLE LOW MISSING (<30%)
    # ========================================
    print("\n📍 Phase 3: Handle LOW missing features (<30%)")
    print("-" * 60)

    # Bathrooms (23.40% missing) - Fill with median grouped by Bedrooms
    if "Bathrooms" in df.columns and "Bedrooms" in df.columns:
        # First fill Bedrooms if it has missing
        if df["Bedrooms"].isna().sum() > 0:
            prep.fill_median("Bedrooms")
        prep.fill_median("Bathrooms", group_by="Bedrooms")
    elif "Bathrooms" in df.columns:
        prep.fill_median("Bathrooms")

    # Legal status (14.91% missing)
    if "Legal status" in df.columns:
        prep.fill_value("Legal status", "Không rõ")

    # Floors (11.92% missing)
    if "Floors" in df.columns:
        prep.fill_mode("Floors")

    # Fill any remaining numeric columns with median
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isna().sum() > 0:
            prep.fill_median(col)

    # ========================================
    # STEP 7: FEATURE ENGINEERING
    # ========================================
    print("\n📍 Phase 4: Feature Engineering")
    print("-" * 60)

    # ❌ REMOVED: Price-based features to avoid target leakage
    # If Price is your target, it should NOT be used in feature engineering

    # Room-related features
    if "Bathrooms" in df.columns and "Bedrooms" in df.columns:
        prep.create_feature(
            "new_bathroom_bedroom_ratio",
            lambda df: df["Bathrooms"] / df["Bedrooms"].replace(0, 1),
            "Bathroom to Bedroom ratio",
        )

        prep.create_feature(
            "new_total_rooms",
            lambda df: df["Bedrooms"] + df["Bathrooms"],
            "Total number of rooms",
        )

    # Area-related features
    if "Area" in df.columns:
        prep.create_feature(
            "new_is_large_house",
            lambda df: (df["Area"] > 140).astype(int),
            "Flag for large houses (>140m²)",
        )

        if "total_rooms" in prep.df.columns:
            prep.create_feature(
                "new_avg_room_size",
                lambda df: df["Area"] / df["total_rooms"].replace(0, 1),
                "Average room size",
            )

    # Luxury indicator
    if "Bathrooms" in df.columns:
        prep.create_feature(
            "new_is_luxury",
            lambda df: (df["Bathrooms"] >= 4).astype(int),
            "Luxury house indicator (4+ bathrooms)",
        )

    # Multi-story indicator
    if "Floors" in df.columns:
        prep.create_feature(
            "new_is_multi_story",
            lambda df: (df["Floors"] > 2).astype(int),
            "Multi-story house indicator",
        )

    # Location features
    if "Address" in df.columns:
        prep.extract_from_address("Address")

    # ========================================
    # STEP 8: CREATE CATEGORICAL FEATURES
    # ========================================
    print("\n📍 Phase 5: Create Categorical Features")
    print("-" * 60)

    # Area categories
    if "Area" in df.columns:
        prep.create_bins(
            "Area", n_bins=5, labels=["Rất nhỏ", "Nhỏ", "Trung bình", "Lớn", "Rất lớn"]
        )

    # ❌ REMOVED: price_segment to avoid target leakage

    # ========================================
    # STEP 9: FINAL CHECKS & SAVE
    # ========================================
    print("\n📍 Phase 6: Final Checks")
    print("-" * 60)

    # Check for remaining missing values
    remaining_missing = prep.df.isnull().sum().sum()
    if remaining_missing > 0:
        print(f"⚠️ Warning: {remaining_missing} missing values remain")
        print(prep.get_missing_summary())
    else:
        print("✅ All missing values have been handled!")

    # Print processing summary
    prep.print_processing_summary()

    # Save processed data
    prep.save_processed_data(output_file)

    # Save processing log to dataset folder
    log_path = output_file.replace(".csv", "_log.txt")
    prep.save_processing_log(log_path)

    # ========================================
    # STEP 10: GENERATE REPORT
    # ========================================
    print("\n" + "=" * 80)
    print("📊 FINAL REPORT")
    print("=" * 80)

    print(f"\n✅ Processing Complete!")
    print(f"   • Input file: {input_file}")
    print(f"   • Output file: {output_file}")
    print(f"   • Original shape: {df.shape}")
    print(f"   • Final shape: {prep.df.shape}")
    print(f"   • New features created: {len(prep.new_features)}")

    # Show sample of key features
    key_features = [
        "Price",
        "Area",
        "new_total_rooms",
        "new_is_luxury",
        "has_frontage",
        "new_has_access_road",
        "new_district",
    ]
    available_features = [f for f in key_features if f in prep.df.columns]

    if available_features:
        print(f"\n📋 Sample of processed data ({available_features[:5]}):")
        print(prep.df[available_features[:5]].head())

    # Data quality metrics
    print("\n📈 Data Quality Metrics:")
    print(
        f"   • Completeness: {100 - (prep.df.isnull().sum().sum() / (prep.df.shape[0] * prep.df.shape[1]) * 100):.2f}%"
    )
    print(
        f"   • Features with binary flags: {len([f for f in prep.new_features if f.startswith('has_')])}"
    )
    print(
        f"   • Engineered features: {len([f for f in prep.new_features if not f.startswith('has_')])}"
    )

    return prep.df


def main():
    """
    Main execution function
    """
    try:
        # Define paths relative to code folder
        input_path = "../../dataset/raw/vietnam_housing_dataset.csv"
        output_path = "../../dataset/processed/vietnam_housing_processed.csv"

        # Run preprocessing pipeline
        df_processed = preprocess_vietnam_housing(
            input_file=input_path, output_file=output_path
        )

        print("\n" + "=" * 80)
        print("🎉 SUCCESS! Dataset is ready for modeling!")
        print("=" * 80)

        # Optional: Show recommendations for next steps
        print("\n📚 NEXT STEPS:")
        print(
            "1. Load processed data: df = pd.read_csv('../dataset/vietnam_housing_processed.csv')"
        )
        print("2. Handle outliers (separate pipeline)")
        print("3. Split into train/test sets")
        print("4. Select features for modeling")
        print("5. Train your models!")
        print("\nExample feature sets to try:")
        print("   • Basic: ['Area', 'Bedrooms', 'Bathrooms', 'Floors']")
        print("   • Enhanced: Basic + ['price_per_m2', 'total_rooms', 'District']")
        print("   • Full: All features including binary flags")

        return df_processed

    except FileNotFoundError:
        print("❌ Error: Dataset file not found!")
        print(
            "Please ensure the dataset file is at: '../dataset/vietnam_housing_dataset.csv'"
        )
        print("\nExpected folder structure:")
        print("  project/")
        print("    ├── code/")
        print("    │   ├── data_preprocessor.py")
        print("    │   └── main_preprocessing.py (current file)")
        print("    └── dataset/")
        print("        └── vietnam_housing_dataset.csv")
        return None
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        return None


def process_with_train_test_split(
    input_file: str | None = None,
    test_size: float = 0.2,
    random_state: int = 42,
):
    """
    SCIENTIFICALLY CORRECT: Split first, then fit encoders/scalers ONLY on train set.
    This prevents data leakage.
    """
    print("\n" + "=" * 80)
    print("🔬 SCIENTIFIC PREPROCESSING: Train/Test Split with Proper Fitting")
    print("=" * 80)

    # 1. Load preprocessed data
    print("\n📂 Loading preprocessed data...")

    # Use default path if not provided
    if input_file is None:
        input_file = str(DATASET_DIR / "vietnam_housing_processed.csv")

    df = pd.read_csv(input_file)
    print(f"   ✅ Loaded {len(df):,} records")
    print(f"   📁 From: {input_file}")

    # 2. Separate features and target
    if "Price" not in df.columns:
        raise ValueError("Price column not found. Cannot proceed.")

    X = df.drop(columns=["Price"])
    y = df["Price"]

    # 3. SPLIT FIRST (This is the key to avoid data leakage!)
    print(f"\n✂️ Splitting data: {int((1-test_size)*100)}% train, {int(test_size*100)}% test...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    print(f"   ✅ Train: {len(X_train):,} samples")
    print(f"   ✅ Test: {len(X_test):,} samples")

    # 4. Identify column types
    print("\n🔍 Analyzing columns...")
    low_cardinality_cats = ["House direction", "Balcony direction", "Legal status",
                            "Area_binned", "Furniture state", "new_city"]
    high_cardinality_cats = ["Address", "new_street_ward", "new_district"]

    # Filter only existing columns
    low_cat = [c for c in low_cardinality_cats if c in X_train.columns]
    high_cat = [c for c in high_cardinality_cats if c in X_train.columns]
    numeric_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()

    print(f"   • Low-cardinality categorical: {len(low_cat)}")
    print(f"   • High-cardinality categorical: {len(high_cat)}")
    print(f"   • Numeric: {len(numeric_cols)}")

    # 5. FIT encoders on TRAIN set only
    print("\n🔧 Fitting encoders on TRAIN set...")
    label_encoders = {}
    for col in high_cat:
        le = LabelEncoder()
        X_train.loc[:, col] = le.fit_transform(X_train[col].astype(str))
        label_encoders[col] = le

        # Transform test (handle unknown categories)
        test_values = X_test[col].astype(str)
        encoded = []
        for val in test_values:
            if val in le.classes_:
                encoded.append(le.transform([val])[0])
            else:
                encoded.append(-1)
        X_test.loc[:, col] = encoded
    print(f"   ✅ Fitted {len(label_encoders)} label encoders")

    # 6. One-hot encode (using get_dummies with sparse for consistency)
    print("\n🔧 Applying one-hot encoding...")
    X_train_ohe = pd.get_dummies(X_train[low_cat], prefix=low_cat)
    X_test_ohe = pd.get_dummies(X_test[low_cat], prefix=low_cat)

    # Align test set columns with train set
    X_test_ohe = X_test_ohe.reindex(columns=X_train_ohe.columns, fill_value=0)
    print(f"   ✅ Created {X_train_ohe.shape[1]} one-hot features")

    # 7. Get remaining columns (numeric + label-encoded)
    remaining_cols = [c for c in X_train.columns if c not in low_cat]
    X_train_remaining = X_train[remaining_cols]
    X_test_remaining = X_test[remaining_cols]

    # 8. Select numeric columns to scale (exclude binary flags)
    cols_to_scale = []
    for col in numeric_cols:
        if col in high_cat:  # Skip label-encoded
            continue
        unique_vals = set(X_train[col].dropna().unique())
        if unique_vals.issubset({0, 1}):  # Skip binary
            continue
        cols_to_scale.append(col)

    print(f"\n🔧 Scaling {len(cols_to_scale)} continuous numeric features...")

    # 9. FIT scaler on TRAIN set only
    scaler = StandardScaler()
    X_train_remaining[cols_to_scale] = scaler.fit_transform(X_train_remaining[cols_to_scale])
    X_test_remaining[cols_to_scale] = scaler.transform(X_test_remaining[cols_to_scale])
    print(f"   ✅ Fitted and applied StandardScaler")

    # 10. Combine all features
    print("\n🔗 Combining all features...")
    X_train_final = pd.concat([X_train_ohe, X_train_remaining], axis=1)
    X_test_final = pd.concat([X_test_ohe, X_test_remaining], axis=1)

    # 11. Save datasets
    print("\n💾 Saving processed datasets...")
    train_df = X_train_final.copy()
    train_df["Price"] = y_train.values
    test_df = X_test_final.copy()
    test_df["Price"] = y_test.values

    # Use absolute paths from DATASET_DIR
    train_path = DATASET_DIR / "train_final.csv"
    test_path = DATASET_DIR / "test_final.csv"
    scaler_path = DATASET_DIR / "scaler.pkl"
    encoders_path = DATASET_DIR / "label_encoders.pkl"

    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    print(f"   ✅ Saved train_final.csv ({train_df.shape})")
    print(f"   ✅ Saved test_final.csv ({test_df.shape})")

    # 12. Save fitted objects for future use
    joblib.dump(scaler, scaler_path)
    joblib.dump(label_encoders, encoders_path)
    print(f"   ✅ Saved scaler and encoders for future use")

    print("\n" + "=" * 80)
    print("✅ SCIENTIFIC PREPROCESSING COMPLETE!")
    print("=" * 80)
    print("\n📊 Summary:")
    print(f"   • Train samples: {len(train_df):,}")
    print(f"   • Test samples: {len(test_df):,}")
    print(f"   • Total features: {X_train_final.shape[1]}")
    print(f"   • Continuous features scaled: {len(cols_to_scale)}")
    print(f"   • Categorical features encoded: {len(low_cat) + len(high_cat)}")

    return train_df, test_df


if __name__ == "__main__":
    # Step 1: Run basic preprocessing (handle missing values, create features)
    processed_df = main()

    # Step 2: Run SCIENTIFIC preprocessing with proper train/test split
    if processed_df is not None:
        train_df, test_df = process_with_train_test_split()
        print("\n🎯 Ready for modeling! Use train_final.csv and test_final.csv")

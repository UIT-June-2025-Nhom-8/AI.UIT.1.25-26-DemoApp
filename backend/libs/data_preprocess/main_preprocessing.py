# main_preprocessing.py
# Main preprocessing pipeline for Vietnam Housing Dataset
# Uses the generic DataPreprocessor class

import pandas as pd
import numpy as np
from data_preprocessor import DataPreprocessor  # Import directly (same folder)
from one_hot_encoding_and_scaler import (
    load_dataset,
    analyze_columns,
    apply_label_encoding,
    apply_one_hot,
    select_numeric_for_scaling,
    scale_numeric_features,
    combine_processed,
    save_dataset,
)
import warnings
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")

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

    # Price-related features
    if "Price" in df.columns and "Area" in df.columns:
        prep.create_feature(
            "new_price_per_m2",
            lambda df: df["Price"] / df["Area"].replace(0, 1),
            "Price per square meter",
        )

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

    # Price segments
    if "Price" in df.columns:
        # Define price ranges based on quartiles
        price_quartiles = df["Price"].quantile([0.25, 0.5, 0.75]).values
        prep.df["price_segment"] = pd.cut(
            prep.df["Price"],
            bins=[0] + list(price_quartiles) + [float("inf")],
            labels=["Bình dân", "Trung cấp", "Cao cấp", "Luxury"],
        )
        prep.new_features.append("price_segment")

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
        "price_per_m2",
        "total_rooms",
        "is_luxury",
        "has_frontage",
        "has_access_road",
        "District",
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


def process_one_hot_and_scale():
    """
    Load data, apply one-hot encoding and scale numeric features.

    Args:
        input_file: Input CSV filename
        output_file: Output CSV filename
    Returns:
        Processed dataframe
    """
    # 1. Load dataset
    df = load_dataset("../../dataset/processed/vietnam_housing_processed.csv")

    # 2. Analyze fields
    numeric_cols, low_cat, high_cat, unprocessed = analyze_columns(df)

    # 3. Label encode
    df_le = apply_label_encoding(df, high_cat)

    # 4. One-hot encode
    df_ohe = apply_one_hot(df_le, low_cat)

    # 5. Remaining columns = numeric + label-encoded + unprocessed
    remaining_cols = [c for c in df_le.columns if c not in low_cat]
    df_remaining = df_le[remaining_cols]

    # 6. Select numeric to scale
    numeric_for_scaler = select_numeric_for_scaling(df_remaining, numeric_cols, high_cat)

    # 7. Apply scaling
    df_scaled, scaler = scale_numeric_features(df_remaining, numeric_for_scaler)

    # 8. Combine final dataset
    df_final = combine_processed(df_ohe, df_scaled)

    # 9. Save
    save_dataset(df_final, "../../dataset/processed/final_preprocessed_dataset.csv")


if __name__ == "__main__":
    # Run the main pipeline
    processed_df = main()
    process_one_hot_and_scale()

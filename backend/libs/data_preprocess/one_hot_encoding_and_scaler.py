import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

# =============================
# LOG FUNCTION
# =============================
def log(msg):
    print(f"[LOG] {msg}")


# =============================
# 1. LOAD DATASET
# =============================
def load_dataset(path):
    log(f"Loading dataset from: {path}")
    df = pd.read_csv(path)
    log(f"Dataset loaded. Shape = {df.shape}")
    return df


# =============================
# 2. ANALYZE COLUMNS
# =============================
def analyze_columns(df):
    log("Analyzing dataset columns...")

    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
    log(f"Numeric columns detected ({len(numeric_cols)}): {numeric_cols}")

    low_cat = [
        "House direction",
        "Balcony direction",
        "Legal status",
        "Area_binned",
        "price_segment",
        "new_district",
    ]
    log(f"Low-cardinality categorical → One-hot encoding: {low_cat}")

    high_cat = ["Address", "new_street_ward"]
    log(f"High-cardinality categorical → Label encoding: {high_cat}")

    processed = set(numeric_cols) | set(low_cat) | set(high_cat)
    unprocessed = list(set(df.columns) - processed)
    log(f"Unprocessed columns (kept as-is): {unprocessed}")

    return numeric_cols, low_cat, high_cat, unprocessed


# =============================
# 3. LABEL ENCODING
# =============================
def apply_label_encoding(df, high_cat):
    df = df.copy()
    for col in high_cat:
        log(f"Label Encoding column '{col}' (text → integer).")
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
    return df


# =============================
# 4. ONE-HOT ENCODING
# =============================
def apply_one_hot(df, low_cat):
    log("Applying One-Hot Encoding using pandas.get_dummies()")
    df_ohe = pd.get_dummies(df[low_cat], prefix=low_cat)
    log(f"Created {df_ohe.shape[1]} one-hot columns.")
    return df_ohe


# =============================
# 5. SELECT NUMERIC FEATURES FOR SCALING
# =============================
def select_numeric_for_scaling(df, numeric_cols, high_cat):
    """
    Select numeric columns that SHOULD be scaled.
    
    RULE:
    - Exclude binary columns (only contain {0,1})
    - Exclude label-encoded categorical columns
    - Scale only real continuous numeric columns
    """
    cols_to_scale = []
    cols_skipped = []

    for col in numeric_cols:

        # 1. Skip label-encoded columns
        if col in high_cat:
            cols_skipped.append(col)
            continue

        unique_vals = set(df[col].dropna().unique())

        # 2. Skip binary columns
        if unique_vals.issubset({0, 1}):
            cols_skipped.append(col)
            continue

        # Otherwise → scale
        cols_to_scale.append(col)

    print("[LOG] Numeric columns detected:", numeric_cols)
    print("[LOG] Skipped (binary + label-encoded):", cols_skipped)
    print("[LOG] Continuous numeric columns (WILL SCALE):", cols_to_scale)

    return cols_to_scale


# =============================
# 6. APPLY STANDARD SCALER
# =============================
def scale_numeric_features(df, numeric_cols):
    log("Applying StandardScaler to selected numeric columns...")

    scaler = StandardScaler()
    df_scaled = df.copy()

    df_scaled[numeric_cols] = scaler.fit_transform(df[numeric_cols])

    log(f"Scaled columns: {numeric_cols}")
    return df_scaled, scaler


# =============================
# 7. COMBINE DATASETS
# =============================
def combine_processed(df_ohe, df_scaled):
    log("Combining one-hot features + scaled numeric + label-encoded + others")
    df_final = pd.concat([df_ohe, df_scaled], axis=1)
    log(f"Final dataset shape = {df_final.shape}")
    return df_final


# =============================
# 8. SAVE FINAL DATASET
# =============================
def save_dataset(df, path):
    log(f"Saving dataset to: {path}")
    df.to_csv(path, index=False)
    log("Save completed.")


# Data Processing Flow: UI Input → Model Prediction

## 📋 Tổng quan

```
UI Fields (13 fields)
    ↓
Backend API
    ↓
Preprocessing Service (mapping + encoding + feature engineering)
    ↓
41 Features DataFrame
    ↓
ML Model (LightGBM/XGBoost/Random Forest)
    ↓
Prediction (VND)
```

---

## 1. Input Fields Mapping

### 1.1 UI Form Fields

| UI Field | Backend Key | Type | Required | Default | Example |
|----------|-------------|------|----------|---------|---------|
| Thành phố | `City` | select | No | "Hồ Chí Minh" | "Hà Nội" |
| Diện tích | `Area` | number | **Yes** | - | 120 |
| Số phòng ngủ | `Bedrooms` | number | No | 2 | 3 |
| Số toilet | `Bathrooms` | number | No | 2 | 2 |
| Số tầng | `Floors` | number | No | 1 | 2 |
| Mặt tiền | `Frontage` | number | No | 0 | 5 |
| Đường vào | `AccessRoad` | number | No | 0 | 4 |
| Quận/Huyện | `District` | text | No | "" | "Quận 7" |
| Phường/Xã | `Ward` | text | No | "" | "Phường Tân Phú" |
| Đường | `Street` | text | No | "" | "Nguyễn Văn Linh" |
| Hướng nhà | `Direction` | text | No | "" | "Đông Nam" |
| Hướng ban công | `BalconyDirection` | text | No | "" | "Đông" |
| Giấy tờ pháp lý | `LegalStatus` | text | No | "" | "Sổ hồng" |
| Nội thất | `Furniture` | text | No | "" | "Đầy đủ" |

**Request payload:**
```json
{
  "features": {
    "City": "Hà Nội",
    "Area": 120,
    "Bedrooms": 3,
    "Bathrooms": 2,
    "District": "Ba Đình",
    // ... rest
  },
  "use_ensemble": true
}
```

---

## 2. Preprocessing Pipeline

### 2.1 Step-by-Step Flow

```python
# File: tree_preprocess_service.py:148

def preprocess(data: Dict[str, Any]) -> pd.DataFrame:
    """
    Transform 13 input fields → 41 model features

    Process:
    1. Extract & validate basic fields
    2. Encode categorical fields (with fallback for unknowns)
    3. Generate derived features
    4. Generate interaction features
    5. Add location-based statistics
    6. Return 1-row DataFrame with 41 columns
    """
```

---

### 2.2 Field Processing Details

#### **A. Numeric Fields** (Direct Mapping)

| Input Field | Output Feature | Processing | Default |
|-------------|----------------|------------|---------|
| `Area` | `Area` | `float(value)` | 70.0 |
| `Frontage` | `Frontage` | `float(value)` | 0.0 |
| `AccessRoad` | `Access Road` | `float(value)` | 0.0 |
| `Floors` | `Floors` | `float(value)` | 1.0 |
| `Bedrooms` | `Bedrooms` | `float(value)` | 2.0 |
| `Bathrooms` | `Bathrooms` | `float(value)` | 2.0 |

**Code:** `tree_preprocess_service.py:161-168`

```python
processed['Area'] = self._to_float(data.get('Area', 70))
processed['Bedrooms'] = self._to_float(data.get('Bedrooms', 2))
# ... similar for other numeric fields
```

---

#### **B. Categorical Fields** (Label Encoding)

##### **B1. Direction Fields**

**Encoding Table:**

| Input Value | Encoded | Notes |
|-------------|---------|-------|
| "Đông", "dong", "East", "e" | 0 | Case-insensitive |
| "Tây", "tay", "West", "w" | 1 | Default if unknown |
| "Nam", "south", "s" | 2 | |
| "Bắc", "bac", "North", "n" | 3 | |
| "Đông Nam", "dong nam", "Southeast" | 4 | |
| "Đông Bắc", "dong bac", "Northeast" | 5 | |
| "Tây Nam", "tay nam", "Southwest" | 6 | |
| "Tây Bắc", "tay bac", "Northwest" | 7 | |
| **Unknown / Empty** | **1** | **Fallback to "Tây"** |

**Code:** `tree_preprocess_service.py:310-318`

```python
# Input: Direction="Đông Nam"
processed['House direction'] = self._encode_direction("Đông Nam")  # → 4

# Input: Direction="Invalid"
processed['House direction'] = self._encode_direction("Invalid")   # → 1 (fallback)
```

**Fields using this encoding:**
- `Direction` → `House direction`
- `BalconyDirection` → `Balcony direction`

---

##### **B2. Legal Status**

| Input Value | Encoded | Notes |
|-------------|---------|-------|
| "Sổ đỏ", "so do" | 0 | Default if unknown |
| "Sổ hồng", "so hong" | 1 | |
| "Hợp đồng", "hop dong" | 2 | |
| "Đang chờ sổ", "dang cho so" | 3 | |
| "Không rõ", "khong ro" | 4 | |
| **Unknown / Empty** | **0** | **Fallback to "Sổ đỏ"** |

**Code:** `tree_preprocess_service.py:319-327`

---

##### **B3. Furniture State**

| Input Value | Encoded | Notes |
|-------------|---------|-------|
| "Cao cấp", "cao cap", "Full" | 0 | |
| "Đầy đủ", "day du", "Basic" | 1 | Default if unknown |
| "Cơ bản", "co ban" | 2 | |
| "Không nội thất", "khong noi that", "None", "Trống" | 3 | |
| "Không rõ", "khong ro" | 4 | |
| **Unknown / Empty** | **1** | **Fallback to "Đầy đủ"** |

**Code:** `tree_preprocess_service.py:328-336`

---

#### **C. Location Fields** (Special Handling)

##### **C1. City - Multi-level Fallback**

**Processing Logic:**

```python
# Priority order:
1. User-selected City from dropdown
   ↓ (if empty)
2. Auto-detect from District using DISTRICT_TO_CITY mapping
   ↓ (if no match)
3. Default to "Hồ Chí Minh"
   ↓
4. Normalize (handle variations like "HCM", "hồ chí minh")
   ↓
5. Label encode
```

**Supported Cities (Model-optimized):**

| City | Training % | Auto-detect Districts | Fallback Encoding |
|------|-----------|----------------------|-------------------|
| Hồ Chí Minh | 38.5% | 23 districts (Quận 1-12, Gò Vấp, Bình Tân, Thủ Đức, ...) | Encoded value depends on LabelEncoder |
| Hà Nội | 33.1% | 13 districts (Ba Đình, Hoàn Kiếm, Đống Đa, Hà Đông, ...) | |
| Bình Dương | 5.5% | 5 districts (Thủ Dầu Một, Dĩ An, Thuận An, ...) | |
| Đà Nẵng | 4.7% | 6 districts (Hải Châu, Thanh Khê, Sơn Trà, ...) | |
| **Other cities** | 22.3% | **Not mapped** | **Hash encoding or -1** |

**Code:** `tree_preprocess_service.py:197-209, 310-340`

**Examples:**

```python
# Case 1: User selects city
Input: {"City": "Hà Nội", "District": "Ba Đình"}
→ City = "Hà Nội" (from user input)

# Case 2: Auto-detect from district
Input: {"District": "Ba Đình"}  # City not provided
→ City = "Hà Nội" (auto-detected from DISTRICT_TO_CITY["Ba Đình"])
→ Log: "Auto-detected city 'Hà Nội' from district 'Ba Đình'"

# Case 3: Unknown district
Input: {"District": "Some Unknown District"}
→ City = "Hồ Chí Minh" (fallback)

# Case 4: City variation
Input: {"City": "hcm"}  # Lowercase abbreviation
→ City = "Hồ Chí Minh" (normalized via CITY_MAPPING)
```

---

##### **C2. District & Ward - Label Encoding with Fallback**

**Processing:**

```python
def _encode_categorical(self, column: str, value: str) -> int:
    """
    Encode using pre-fitted LabelEncoder from training data.

    If value is unknown (not in encoder.classes_):
        → Return -1 (tree models can handle this)

    If no encoder available:
        → Hash encoding: abs(hash(value)) % 1000
    """
```

**Code:** `tree_preprocess_service.py:337-352`

**Examples:**

```python
# Known district (in training data)
Input: {"District": "Quận 7"}
→ new_district = 15 (from LabelEncoder)

# Unknown district (not in training data)
Input: {"District": "District XYZ"}
→ new_district = -1 (unknown category flag)
# Tree models handle -1 gracefully

# Ward encoding (similar logic)
Input: {"Ward": "Phường Tân Phú"}
→ new_street_ward = 234 (from LabelEncoder or hash)
```

**Impact of Unknown Values:**

| Scenario | Encoding | Model Behavior | Prediction Quality |
|----------|----------|----------------|-------------------|
| Known district (trong training data) | Exact encoded value | Optimal | ⭐⭐⭐⭐⭐ |
| Unknown district (không trong training) | -1 or hash | Uses fallback logic | ⭐⭐⭐ Fair |
| Empty district | 0 | Uses defaults | ⭐⭐ Poor |

---

## 3. Feature Engineering (13 → 41 Features)

### 3.1 Feature Categories

| Category | Count | Source | Purpose |
|----------|-------|--------|---------|
| **Basic** | 10 | Direct from input | Area, Frontage, Access Road, Directions, Floors, Bedrooms, Bathrooms, Legal status, Furniture |
| **Location** | 3 | Encoded | City, District, Ward |
| **Binary Flags** | 4 | Derived | has_balcony_direction, has_house_direction, has_access_road, has_frontage |
| **Ratios & Stats** | 6 | Computed | bathroom_bedroom_ratio, total_rooms, is_large_house, avg_room_size, is_luxury, is_multi_story |
| **Area Binning** | 1 | Derived | Area_binned (0-4 for 5 bins) |
| **Interactions** | 5 | Products | area_x_bathrooms, area_x_bedrooms, area_x_floors, bedrooms_x_bathrooms, bedrooms_x_floors |
| **Luxury Score** | 1 | Computed | luxury_score (0-3) |
| **City-Specific** | 4 | Conditional | area_in_hồ_chí_minh, area_in_hà_nội, area_in_bình_dương, area_in_đà_nẵng |
| **Quality Metrics** | 2 | Derived | room_density, access_quality |
| **District Stats** | 7 | Pre-computed | district_area_mean, district_area_median, district_area_std, district_sample_count, district_tier |

**Total:** 41 features

---

### 3.2 Critical Derived Features

#### **Binary Flags** (Code: line 188-191)

```python
new_has_balcony_direction = 1 if BalconyDirection else 0
new_has_house_direction = 1 if Direction else 0
new_has_access_road = 1 if AccessRoad > 0 else 0
has_frontage = 1 if Frontage > 0 else 0
```

#### **City-Specific Area Features** (Code: line 246-250)

```python
# Only ONE of these is non-zero based on detected city
area_in_hồ_chí_minh = Area if City == "Hồ Chí Minh" else 0
area_in_hà_nội = Area if City == "Hà Nội" else 0
area_in_bình_dương = Area if City == "Bình Dương" else 0
area_in_đà_nẵng = Area if City == "Đà Nẵng" else 0
```

**Impact for Unknown City:**

```python
# If City = "Vũng Tàu" (not in 4 main cities)
area_in_hồ_chí_minh = 0  # All city-specific features = 0
area_in_hà_nội = 0
area_in_bình_dương = 0
area_in_đà_nẵng = 0
# Model loses city-specific signal → prediction less accurate
```

#### **District Statistics** (Code: line 258-273)

**Source:** Pre-computed from training data (`location_stats_optimized.pkl`)

```python
if district in location_stats:
    # Use actual statistics from training data
    new_district_area_mean = stats['area_mean']       # e.g., 95.5 for Quận 7
    new_district_area_median = stats['area_median']   # e.g., 90.0
    new_district_area_std = stats['area_std']         # e.g., 45.2
    new_district_sample_count = stats['sample_count'] # e.g., 523
    new_district_tier = stats['tier']                 # 0-4, e.g., 1 for premium
else:
    # Unknown district: use default median values
    new_district_area_mean = 70.0
    new_district_area_median = 65.0
    new_district_area_std = 30.0
    new_district_sample_count = 100
    new_district_tier = 2  # Middle tier
```

**Impact:**

| District Status | Stats Source | Prediction Quality |
|----------------|--------------|-------------------|
| Known district (in training) | Real statistics | ⭐⭐⭐⭐⭐ Best |
| Unknown district | Default median values | ⭐⭐⭐ Fair |

---

## 4. Unknown Value Handling Summary

### 4.1 Fallback Strategy Table

| Field Type | Unknown Value Handling | Fallback Value | Impact on Prediction |
|-----------|------------------------|----------------|---------------------|
| **Numeric** (Area, Bedrooms, etc.) | Use default | 70, 2, 2, 1, 0, 0 | ⭐⭐ Poor if wrong |
| **Direction** | Fallback encoding | 1 ("Tây") | ⭐⭐⭐ Minor |
| **Legal Status** | Fallback encoding | 0 ("Sổ đỏ") | ⭐⭐⭐ Minor |
| **Furniture** | Fallback encoding | 1 ("Đầy đủ") | ⭐⭐⭐ Minor |
| **City** (not in 4 main) | Label encode or hash | Hash value | ⭐⭐ Poor (no city-specific features) |
| **District** (unknown) | -1 or hash | -1 | ⭐⭐⭐ Fair (uses default stats) |
| **Ward** (unknown) | -1 or hash | -1 | ⭐⭐⭐⭐ Minor impact |

### 4.2 Example: Complete Unknown Input

```python
# Worst case: minimal input with unknowns
Input = {
    "Area": 100,
    "City": "Cần Thơ",           # Not in 4 main cities
    "District": "Ninh Kiều",      # Unknown district
    "Direction": "InvalidDir",    # Unknown direction
}

# Processing result:
City = "Cần Thơ" → Encoded (hash or -1)
  → area_in_hồ_chí_minh = 0     # ❌ No city-specific signal
  → area_in_hà_nội = 0
  → area_in_bình_dương = 0
  → area_in_đà_nẵng = 0

District = "Ninh Kiều" → -1 or hash
  → new_district_area_mean = 70.0   # ⚠️ Default values
  → new_district_tier = 2

Direction = "InvalidDir" → 1       # Fallback to "Tây"

# Model can still predict, but accuracy is lower
# Expected: ⭐⭐⭐ Fair prediction (lacks location signals)
```

---

## 5. Model Prediction

### 5.1 Input to Model

**Format:** DataFrame with 1 row × 41 columns

```python
features_df = pd.DataFrame([{
    "Area": 120.0,
    "Frontage": 5.0,
    "Access Road": 4.0,
    "House direction": 4,         # Encoded
    "Balcony direction": 0,       # Encoded
    "Floors": 2.0,
    "Bedrooms": 3.0,
    "Bathrooms": 2.0,
    "Legal status": 1,            # Encoded
    "Furniture state": 1,         # Encoded
    "new_has_balcony_direction": 1,
    "new_has_house_direction": 1,
    "new_city": 15,               # Encoded
    "new_district": 87,           # Encoded
    "new_street_ward": 234,       # Encoded
    # ... 26 more features
}])
```

### 5.2 Model Processing

**For LightGBM:** Column names must use underscores

```python
# Rename for LightGBM compatibility
"Access Road" → "Access_Road"
"House direction" → "House_direction"
"Balcony direction" → "Balcony_direction"
"Legal status" → "Legal_status"
"Furniture state" → "Furniture_state"
```

**Code:** `tree_model_service.py:166-174`

### 5.3 Prediction Output

```python
prediction = model.predict(features_df)[0]  # e.g., 3500000000 (3.5 tỷ VND)
confidence = max(70, min(95, r2_score * 100))  # e.g., 89%

return {
    "prediction": 3500000000,
    "prediction_formatted": "3.500.000.000 ₫",
    "confidence": 89.0,
    "model_used": "lightgbm"
}
```

---

## 6. Quality Prediction Guidelines

### 6.1 Input Quality → Prediction Quality

| Input Quality | Characteristics | Expected Confidence | Example |
|--------------|----------------|---------------------|---------|
| **Excellent** ⭐⭐⭐⭐⭐ | City in top 4, known district, complete data | 85-95% | HCM, Quận 7, all fields filled |
| **Good** ⭐⭐⭐⭐ | City in top 4, unknown district | 75-85% | HCM, unknown district |
| **Fair** ⭐⭐⭐ | City outside top 4, or missing many fields | 65-75% | Cần Thơ, Ninh Kiều |
| **Poor** ⭐⭐ | Only Area provided, all defaults | 50-65% | Only Area=100 |

### 6.2 Recommendations for Best Accuracy

**Must have:**
- ✅ Area (required)
- ✅ City (select from 4 main cities)
- ✅ District (enter correctly)

**Should have:**
- ⭐ Bedrooms, Bathrooms (strong signal)
- ⭐ Frontage, AccessRoad (location quality)
- ⭐ Floors (building type)

**Nice to have:**
- Direction, BalconyDirection
- LegalStatus, Furniture
- Ward, Street

---

## 7. Complete Flow Example

### Input:
```json
{
  "City": "Hà Nội",
  "Area": 100,
  "Bedrooms": 3,
  "Bathrooms": 2,
  "District": "Ba Đình",
  "Direction": "Đông Nam"
}
```

### Preprocessing:
```python
# Step 1: Basic features
Area = 100.0
Bedrooms = 3.0
Bathrooms = 2.0
Floors = 1.0 (default)
Frontage = 0.0 (default)
Access Road = 0.0 (default)

# Step 2: Encode categorical
House direction = 4 ("Đông Nam")
Balcony direction = 1 (default "Tây")
Legal status = 0 (default "Sổ đỏ")
Furniture state = 1 (default "Đầy đủ")

# Step 3: Location
City = "Hà Nội" → new_city = 8 (encoded)
District = "Ba Đình" → new_district = 42 (encoded)
Ward = "" → new_street_ward = 0 (default)

# Step 4: Binary flags
new_has_house_direction = 1
new_has_balcony_direction = 0
new_has_access_road = 0
has_frontage = 0

# Step 5: Derived features
new_bathroom_bedroom_ratio = 2/3 = 0.667
new_total_rooms = 3 + 2 = 5
new_is_large_house = 0 (100 < 140)
new_avg_room_size = 100/5 = 20.0
new_is_luxury = 0 (bathrooms < 4)
new_is_multi_story = 0 (floors <= 2)
Area_binned = 2 (60-100 range)

# Step 6: Interactions
area_x_bathrooms = 100 * 2 = 200
area_x_bedrooms = 100 * 3 = 300
area_x_floors = 100 * 1 = 100
bedrooms_x_bathrooms = 3 * 2 = 6
bedrooms_x_floors = 3 * 1 = 3
luxury_score = 1 (area>100: 0, bathrooms<3: 0, furniture: +1)

# Step 7: City-specific
area_in_hồ_chí_minh = 0
area_in_hà_nội = 100  ← Active
area_in_bình_dương = 0
area_in_đà_nẵng = 0

# Step 8: Quality
room_density = 5/100 = 0.05
access_quality = 0 (no access road)

# Step 9: District stats (Ba Đình in training data)
new_district_area_mean = 85.2
new_district_area_median = 80.0
new_district_area_std = 35.4
new_district_sample_count = 450
new_district_tier = 1 (premium area)
```

### Model Input:
```python
DataFrame: 1 row × 41 columns
[100.0, 0.0, 0.0, 4, 1, 1.0, 3.0, 2.0, 0, 1, 0, 1, 8, 42, 0, 0, 0,
 0.667, 5.0, 0, 20.0, 0, 0, 2, 200.0, 300.0, 100.0, 6.0, 3.0, 1,
 0.0, 100.0, 0.0, 0.0, 0.05, 0, 85.2, 80.0, 35.4, 450, 1]
```

### Output:
```json
{
  "prediction": 2800000000,
  "prediction_formatted": "2.800.000.000 ₫",
  "confidence": 87.5,
  "model_used": "lightgbm"
}
```

---

## 8. Technical References

| Component | File | Key Functions |
|-----------|------|---------------|
| **API Routes** | `app/api/routes.py:205` | `/predict`, `/parse-and-predict` |
| **Preprocessing** | `app/services/tree_preprocess_service.py:148` | `preprocess()` |
| **Encoding** | `tree_preprocess_service.py:310-352` | `_encode_direction()`, `_encode_legal_status()`, `_encode_furniture()`, `_auto_detect_city_from_district()`, `_encode_categorical()` |
| **Model Service** | `app/services/tree_model_service.py:132` | `predict()`, `predict_all_models()` |
| **Feature List** | `tree_preprocess_service.py:21-63` | `EXPECTED_FEATURES` |

---

**Last Updated:** 2025-12-28
**Version:** 2.0.0

# Luồng Xử lý Dữ liệu: UI → Model Prediction

> **📖 Chi tiết Technical:** Xem [DATA_PROCESSING_FLOW.md](DATA_PROCESSING_FLOW.md) để hiểu đầy đủ về:
> - Xử lý từng loại field (numeric, categorical, location)
> - Fallback strategies cho unknown values
> - Feature engineering (13 → 41 features)
> - Complete flow example với code references

---

## 📋 Tổng quan

Hệ thống dự đoán giá nhà Việt Nam sử dụng 3 tree-based models (LightGBM, XGBoost, Random Forest) với 41 engineered features.

**Pipeline:**
```
UI (13 fields) → Preprocessing (encode + engineer) → 41 Features → Model → Price (VND)
```

---

## 1. Architecture

### 1.1 System Components

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐
│   UI Form   │────▶│  API Routes  │────▶│ Preprocess  │────▶│  Models  │
│ (React/TS)  │     │  (FastAPI)   │     │   Service   │     │(LightGBM)│
└─────────────┘     └──────────────┘     └─────────────┘     └──────────┘
                           │                     │                  │
                           │                     │                  ▼
                           ▼                     │           ┌──────────────┐
                    ┌──────────────┐            │           │  Prediction  │
                    │ LLM Service  │            │           │   3.5 tỷ VND │
                    │ (Parse Text) │            │           └──────────────┘
                    └──────────────┘            │
                                                 ▼
                                        ┌─────────────────┐
                                        │ Feature         │
                                        │ Engineering     │
                                        │ 13 → 41 features│
                                        └─────────────────┘
```

### 1.2 Key Services

| Service | File | Responsibility |
|---------|------|---------------|
| **API** | [routes.py:205](backend/app/api/routes.py#L205) | Orchestrate services, validate requests |
| **LLM Parser** | [llm_service.py:61](backend/app/services/llm_service.py#L61) | Parse Vietnamese text → structured features |
| **Preprocessor** | [tree_preprocess_service.py:148](backend/app/services/tree_preprocess_service.py#L148) | 13 fields → 41 features (encode + derive) |
| **Model Service** | [tree_model_service.py:132](backend/app/services/tree_model_service.py#L132) | Load models, make predictions |

---

## 2. Input Handling

### 2.1 Two Input Methods

| Method | Input | Processing | Use Case |
|--------|-------|------------|----------|
| **Form** | 13 structured fields | Direct preprocessing | User fills form manually |
| **Text** | Vietnamese description | LLM parse → structured → preprocess | User pastes property description |

### 2.2 Form Fields (13 fields)

**Required:**
- ✅ Area (m²)

**Optional but Important:**
- City (dropdown: HCM, Hà Nội, Bình Dương, Đà Nẵng)
- District, Ward
- Bedrooms, Bathrooms, Floors
- Frontage, AccessRoad
- Direction, BalconyDirection
- LegalStatus, Furniture
- Street

**Code:** [FeatureFormStep.tsx:50-72](frontend/src/components/predict/FeatureFormStep.tsx#L50)

### 2.3 City Field Handling

**⚠️ Critical for Accuracy:**

| Input Type | City Source | Fallback | Code |
|-----------|-------------|----------|------|
| Form + City selected | User dropdown | - | Direct |
| Form + No city + Known district | Auto-detect from district | Default HCM | [tree_preprocess_service.py:198-203](backend/app/services/tree_preprocess_service.py#L198) |
| Form + No city + Unknown district | - | Default HCM | Fallback |
| Text input | LLM extraction | Default HCM | [llm_parse.py:160](backend/libs/llm_parse.py#L160) |

**Training Data Coverage:**
- Hồ Chí Minh: 38.5% (11,628 samples)
- Hà Nội: 33.1% (9,996 samples)
- Bình Dương: 5.5% (1,655 samples)
- Đà Nẵng: 4.7% (1,411 samples)

**→ Model optimized for these 4 cities (82% training data)**

---

## 3. Preprocessing Overview

### 3.1 Transformation Pipeline

```
13 Input Fields
    ↓
┌─────────────────────────────────────┐
│ 1. Basic Mapping                    │
│    - Numeric: float conversion      │
│    - Defaults if missing            │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. Categorical Encoding             │
│    - Direction: 0-7                 │
│    - Legal Status: 0-4              │
│    - Furniture: 0-4                 │
│    - City/District/Ward: Label      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. Feature Engineering              │
│    - Binary flags (4)               │
│    - Ratios & counts (6)            │
│    - Area binning (1)               │
│    - Interactions (5)               │
│    - City-specific (4)              │
│    - Quality metrics (2)            │
│    - District stats (7)             │
└─────────────────────────────────────┘
    ↓
41 Features DataFrame
```

**Code:** [tree_preprocess_service.py:148-292](backend/app/services/tree_preprocess_service.py#L148)

### 3.2 Feature Breakdown

| Category | Count | Examples |
|----------|-------|----------|
| Basic | 10 | Area, Frontage, Access Road, House direction, Floors, Bedrooms, Bathrooms, Legal status, Furniture |
| Location | 3 | City (encoded), District (encoded), Ward (encoded) |
| Binary Flags | 4 | has_balcony_direction, has_house_direction, has_access_road, has_frontage |
| Derived | 6 | bathroom_bedroom_ratio, total_rooms, is_large_house, avg_room_size, is_luxury, is_multi_story |
| Area Binned | 1 | Area_binned (0-4 for size categories) |
| Interactions | 5 | area_x_bathrooms, area_x_bedrooms, area_x_floors, bedrooms_x_bathrooms, bedrooms_x_floors |
| Luxury Score | 1 | luxury_score (0-3 based on bathrooms, area, furniture) |
| City-Specific | 4 | area_in_hồ_chí_minh, area_in_hà_nội, area_in_bình_dương, area_in_đà_nẵng |
| Quality | 2 | room_density, access_quality |
| District Stats | 7 | district_area_mean, district_area_median, district_area_std, district_sample_count, district_tier |

**Total: 41 features**

**Full list:** [tree_preprocess_service.py:21-63](backend/app/services/tree_preprocess_service.py#L21)

---

## 4. Handling Unknown/Missing Values

> **📖 Detailed strategies:** See [DATA_PROCESSING_FLOW.md Section 4](DATA_PROCESSING_FLOW.md#4-unknown-value-handling-summary)

### 4.1 Summary Table

| Field Type | Unknown Value | Fallback | Impact |
|-----------|---------------|----------|--------|
| **Numeric** (Area, Bedrooms, ...) | Empty/null | Default values (70, 2, 2, 1, 0, 0) | ⭐⭐ |
| **Direction** | Invalid text | 1 ("Tây") | ⭐⭐⭐ |
| **Legal Status** | Invalid text | 0 ("Sổ đỏ") | ⭐⭐⭐ |
| **Furniture** | Invalid text | 1 ("Đầy đủ") | ⭐⭐⭐ |
| **City** (not in top 4) | e.g., "Cần Thơ" | Encoded, but city-specific features = 0 | ⭐⭐ |
| **District** (unknown) | Not in training | -1 or hash → default district stats | ⭐⭐⭐ |
| **Ward** (unknown) | Not in training | -1 or hash | ⭐⭐⭐⭐ |

**Legend:**
- ⭐⭐⭐⭐⭐ = No impact
- ⭐⭐⭐⭐ = Minor impact
- ⭐⭐⭐ = Fair impact
- ⭐⭐ = Significant impact (lower accuracy)

### 4.2 Critical Insights

**For Best Accuracy:**
1. ✅ Select City from dropdown (4 main cities)
2. ✅ Enter District correctly (especially for HCM/Hanoi common districts)
3. ✅ Provide Bedrooms & Bathrooms (strong signal)

**Model Can Handle:**
- Missing optional fields (uses defaults)
- Unknown directions/legal status (uses fallback encoding)
- Unknown districts (uses default statistics)

**Model Struggles With:**
- Cities outside top 4 (loses city-specific features)
- Only Area provided (too many defaults)

---

## 5. Model Prediction

### 5.1 Supported Models

| Model | File Pattern | Algorithm | Default |
|-------|--------------|-----------|---------|
| LightGBM | `lightgbm_regressor_*.pkl` | Gradient Boosting | ✅ Yes |
| XGBoost | `xgboost_regressor_*.pkl` | Gradient Boosting | No |
| Random Forest | `random_forest_regressor_*.pkl` | Random Forest | No |

**Code:** [tree_model_service.py:66-71](backend/app/services/tree_model_service.py#L66)

### 5.2 Prediction Modes

**Single Model:**
```json
{
  "features": {...},
  "use_ensemble": false,
  "model_name": "lightgbm"
}
→ Returns: prediction, confidence, model_used
```

**Ensemble (Recommended):**
```json
{
  "features": {...},
  "use_ensemble": true
}
→ Returns: average of all 3 models + std deviation
```

**Code:** [routes.py:202-233](backend/app/api/routes.py#L202)

---

## 6. Output Response

### 6.1 Single Model Response

```json
{
  "prediction": 3500000000,
  "prediction_formatted": "3.500.000.000 ₫",
  "confidence": 89.0,
  "model_used": "lightgbm",
  "features_used": {...}
}
```

### 6.2 Ensemble Response

```json
{
  "ensemble_prediction": 3480000000,
  "ensemble_prediction_formatted": "3.480.000.000 ₫",
  "ensemble_std": 120000000,
  "confidence": 88.5,
  "individual_predictions": {
    "lightgbm": {"prediction": 3500000000, "confidence": 89.0},
    "xgboost": {"prediction": 3460000000, "confidence": 87.5},
    "random_forest": {"prediction": 3480000000, "confidence": 89.0}
  },
  "models_used": ["lightgbm", "xgboost", "random_forest"],
  "features_used": {...}
}
```

**Confidence Calculation:**
```python
confidence = max(70, min(95, model.r2_score * 100))
```

**Code:** [tree_model_service.py:180-189](backend/app/services/tree_model_service.py#L180)

---

## 7. Prediction Quality Guidelines

### 7.1 Input Quality → Expected Accuracy

| Scenario | Characteristics | Confidence | Example |
|----------|----------------|------------|---------|
| **Excellent** ⭐⭐⭐⭐⭐ | City in top 4 + Known district + Complete data | 85-95% | HCM, Quận 7, all fields |
| **Good** ⭐⭐⭐⭐ | City in top 4 + Unknown district | 75-85% | HCM, unknown district |
| **Fair** ⭐⭐⭐ | City outside top 4 OR many missing fields | 65-75% | Cần Thơ, Ninh Kiều |
| **Poor** ⭐⭐ | Only Area provided | 50-65% | Area=100, all defaults |

### 7.2 Recommendations

**Must Provide:**
- Area (required)
- City (select from dropdown)

**Should Provide:**
- District (important for location stats)
- Bedrooms, Bathrooms (strong signals)
- Floors (building type)

**Nice to Have:**
- Frontage, AccessRoad (location quality)
- Direction, LegalStatus, Furniture

---

## 8. Quick Reference

### 8.1 File Structure

```
demo/
├── backend/
│   ├── app/
│   │   ├── api/routes.py              # API endpoints
│   │   ├── services/
│   │   │   ├── tree_preprocess_service.py  # 13→41 features
│   │   │   ├── tree_model_service.py       # Model loading/prediction
│   │   │   └── llm_service.py              # Text parsing
│   │   └── schemas/                   # Request/Response types
│   └── models/                        # Trained models (.pkl)
└── frontend/
    └── src/
        ├── components/predict/
        │   └── FeatureFormStep.tsx   # UI form
        └── types/index.ts             # TypeScript types
```

### 8.2 Key Constants

| Constant | Location | Values |
|----------|----------|--------|
| SUPPORTED_CITIES | [FeatureFormStep.tsx:47](frontend/src/components/predict/FeatureFormStep.tsx#L47) | ["Hồ Chí Minh", "Hà Nội", "Bình Dương", "Đà Nẵng"] |
| EXPECTED_FEATURES | [tree_preprocess_service.py:21](backend/app/services/tree_preprocess_service.py#L21) | 41 feature names |
| DISTRICT_TO_CITY | [tree_preprocess_service.py:90](backend/app/services/tree_preprocess_service.py#L90) | 47 district mappings |
| DIRECTION_MAPPING | [tree_preprocess_service.py:148](backend/app/services/tree_preprocess_service.py#L148) | 8 directions (0-7) |

---

## 9. Related Documentation

- **📖 [DATA_PROCESSING_FLOW.md](DATA_PROCESSING_FLOW.md)** - Complete technical flow với code examples
- **📝 [CITY_FIELD_IMPLEMENTATION.md](CITY_FIELD_IMPLEMENTATION.md)** - Changelog cho City field feature
- **🔧 [README.md](README.md)** - Setup & deployment guide

---

**Version:** 2.0.0
**Last Updated:** 2025-12-28
**Status:** ✅ Production Ready

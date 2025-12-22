"""
Tree-Optimized Preprocessing Service
Prepares input data for tree-based models (LightGBM, XGBoost, Random Forest)

This service matches the preprocessing from tree_optimized_preprocessing.py:
- 41 features with label encoding (NOT one-hot)
- Interaction features
- Location-based features
"""
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Feature names expected by the trained models (41 features)
# IMPORTANT: Order must match the trained models from notebooks/models/saved_models
EXPECTED_FEATURES = [
    "Area",
    "Frontage",
    "Access Road",
    "House direction",
    "Balcony direction",
    "Floors",
    "Bedrooms",
    "Bathrooms",
    "Legal status",
    "Furniture state",
    "new_has_balcony_direction",
    "new_has_house_direction",
    "new_city",                      # Fixed: Position 13 (was 15)
    "new_district",                  # Fixed: Position 14 (was 16)
    "new_street_ward",               # Fixed: Position 15 (was 17)
    "new_has_access_road",           # Fixed: Position 16 (was 13)
    "has_frontage",                  # Fixed: Position 17 (was 14)
    "new_bathroom_bedroom_ratio",
    "new_total_rooms",
    "new_is_large_house",
    "new_avg_room_size",
    "new_is_luxury",
    "new_is_multi_story",
    "Area_binned",
    "area_x_bathrooms",
    "area_x_bedrooms",
    "area_x_floors",
    "bedrooms_x_bathrooms",
    "bedrooms_x_floors",
    "luxury_score",
    "area_in_hồ_chí_minh",
    "area_in_hà_nội",
    "area_in_bình_dương",
    "area_in_đà_nẵng",
    "room_density",
    "access_quality",
    "new_district_area_mean",
    "new_district_area_median",
    "new_district_area_std",
    "new_district_sample_count",
    "new_district_tier",
]

# City name mappings (Vietnamese variations)
CITY_MAPPING = {
    # Hồ Chí Minh variations
    "hồ chí minh": "Hồ Chí Minh",
    "ho chi minh": "Hồ Chí Minh",
    "hcm": "Hồ Chí Minh",
    "tphcm": "Hồ Chí Minh",
    "tp hcm": "Hồ Chí Minh",
    "saigon": "Hồ Chí Minh",
    "sài gòn": "Hồ Chí Minh",
    # Hà Nội variations
    "hà nội": "Hà Nội",
    "ha noi": "Hà Nội",
    "hanoi": "Hà Nội",
    # Bình Dương variations
    "bình dương": "Bình Dương",
    "binh duong": "Bình Dương",
    # Đà Nẵng variations
    "đà nẵng": "Đà Nẵng",
    "da nang": "Đà Nẵng",
    "danang": "Đà Nẵng",
}

# House direction mapping
DIRECTION_MAPPING = {
    "đông": 0, "dong": 0, "east": 0, "e": 0,
    "tây": 1, "tay": 1, "west": 1, "w": 1,
    "nam": 2, "south": 2, "s": 2,
    "bắc": 3, "bac": 3, "north": 3, "n": 3,
    "đông nam": 4, "dong nam": 4, "southeast": 4, "se": 4,
    "đông bắc": 5, "dong bac": 5, "northeast": 5, "ne": 5,
    "tây nam": 6, "tay nam": 6, "southwest": 6, "sw": 6,
    "tây bắc": 7, "tay bac": 7, "northwest": 7, "nw": 7,
}

# Legal status mapping
LEGAL_STATUS_MAPPING = {
    "sổ đỏ": 0, "so do": 0,
    "sổ hồng": 1, "so hong": 1,
    "hợp đồng": 2, "hop dong": 2,
    "đang chờ sổ": 3, "dang cho so": 3,
    "không rõ": 4, "khong ro": 4,
}

# Furniture state mapping
FURNITURE_MAPPING = {
    "cao cấp": 0, "cao cap": 0, "full": 0,
    "đầy đủ": 1, "day du": 1, "basic": 1,
    "cơ bản": 2, "co ban": 2,
    "không nội thất": 3, "khong noi that": 3, "none": 3, "trống": 3,
    "không rõ": 4, "khong ro": 4,
}


class TreePreprocessService:
    """
    Service for preprocessing input data for tree-based models.
    Matches the preprocessing from tree_optimized_preprocessing.py
    """

    def __init__(self, encoders_path: Optional[Path] = None, location_stats_path: Optional[Path] = None):
        """
        Initialize service with optional pre-fitted encoders and location stats.
        
        If not provided, will use fallback encoding (label mapping).
        """
        self.label_encoders = {}
        self.location_stats = None
        
        if encoders_path and encoders_path.exists():
            try:
                self.label_encoders = joblib.load(encoders_path)
                logger.info(f"Loaded {len(self.label_encoders)} label encoders")
            except Exception as e:
                logger.warning(f"Failed to load encoders: {e}")
        
        if location_stats_path and location_stats_path.exists():
            try:
                self.location_stats = joblib.load(location_stats_path)
                logger.info("Loaded location stats")
            except Exception as e:
                logger.warning(f"Failed to load location stats: {e}")

    def preprocess(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        Transform raw input to 41 features matching trained model expectations.
        
        Args:
            data: Raw input dictionary with house features
            
        Returns:
            DataFrame with single row containing 41 features
        """
        # Start with a copy of input
        processed = {}
        
        # === BASIC FEATURES ===
        # Numeric features
        processed['Area'] = self._to_float(data.get('Area', 70))
        processed['Frontage'] = self._to_float(data.get('Frontage', 0))
        processed['Access Road'] = self._to_float(data.get('AccessRoad', data.get('Access Road', 0)))
        processed['Floors'] = self._to_float(data.get('Floors', 1))
        processed['Bedrooms'] = self._to_float(data.get('Bedrooms', 2))
        processed['Bathrooms'] = self._to_float(data.get('Bathrooms', 2))
        
        # === CATEGORICAL FEATURES (Label Encoded) ===
        # House direction
        direction = data.get('Direction', data.get('House direction', ''))
        processed['House direction'] = self._encode_direction(direction)
        
        # Balcony direction
        balcony_dir = data.get('BalconyDirection', data.get('Balcony direction', ''))
        processed['Balcony direction'] = self._encode_direction(balcony_dir)
        
        # Legal status
        legal = data.get('LegalStatus', data.get('Legal status', ''))
        processed['Legal status'] = self._encode_legal_status(legal)
        
        # Furniture state
        furniture = data.get('Furniture', data.get('Furniture state', ''))
        processed['Furniture state'] = self._encode_furniture(furniture)
        
        # === BINARY FLAGS ===
        processed['new_has_balcony_direction'] = 1 if balcony_dir else 0
        processed['new_has_house_direction'] = 1 if direction else 0
        processed['new_has_access_road'] = 1 if processed['Access Road'] > 0 else 0
        processed['has_frontage'] = 1 if processed['Frontage'] > 0 else 0
        
        # === LOCATION FEATURES (Label Encoded) ===
        city = self._normalize_city(data.get('City', data.get('new_city', 'Hồ Chí Minh')))
        district = data.get('District', data.get('new_district', ''))
        ward = data.get('Ward', data.get('new_street_ward', ''))
        
        # Encode city, district, ward (use label encoder if available, else use hash)
        processed['new_city'] = self._encode_categorical('new_city', city)
        processed['new_district'] = self._encode_categorical('new_district', district)
        processed['new_street_ward'] = self._encode_categorical('new_street_ward', ward)
        
        # === DERIVED FEATURES ===
        area = processed['Area']
        bedrooms = max(processed['Bedrooms'], 1)  # Avoid division by zero
        bathrooms = processed['Bathrooms']
        floors = processed['Floors']
        
        # Ratio and count features
        processed['new_bathroom_bedroom_ratio'] = bathrooms / bedrooms
        processed['new_total_rooms'] = bedrooms + bathrooms
        processed['new_is_large_house'] = 1 if area > 140 else 0
        processed['new_avg_room_size'] = area / max(processed['new_total_rooms'], 1)
        processed['new_is_luxury'] = 1 if bathrooms >= 4 else 0
        processed['new_is_multi_story'] = 1 if floors > 2 else 0
        
        # Area binned (0-4 for 5 bins)
        if area < 30:
            processed['Area_binned'] = 0  # Rất nhỏ
        elif area < 60:
            processed['Area_binned'] = 1  # Nhỏ
        elif area < 100:
            processed['Area_binned'] = 2  # Trung bình
        elif area < 150:
            processed['Area_binned'] = 3  # Lớn
        else:
            processed['Area_binned'] = 4  # Rất lớn
        
        # === INTERACTION FEATURES ===
        processed['area_x_bathrooms'] = area * bathrooms
        processed['area_x_bedrooms'] = area * bedrooms
        processed['area_x_floors'] = area * floors
        processed['bedrooms_x_bathrooms'] = bedrooms * bathrooms
        processed['bedrooms_x_floors'] = bedrooms * floors
        
        # Luxury score (0-3)
        luxury_score = 0
        if bathrooms >= 3:
            luxury_score += 1
        if area > 100:
            luxury_score += 1
        if processed['Furniture state'] in [0, 1]:  # Cao cấp or đầy đủ
            luxury_score += 1
        processed['luxury_score'] = luxury_score
        
        # === CITY-SPECIFIC AREA FEATURES ===
        processed['area_in_hồ_chí_minh'] = area if city == 'Hồ Chí Minh' else 0
        processed['area_in_hà_nội'] = area if city == 'Hà Nội' else 0
        processed['area_in_bình_dương'] = area if city == 'Bình Dương' else 0
        processed['area_in_đà_nẵng'] = area if city == 'Đà Nẵng' else 0
        
        # === DENSITY & QUALITY FEATURES ===
        processed['room_density'] = processed['new_total_rooms'] / max(area, 1)
        processed['access_quality'] = 0 if processed['Access Road'] == 0 else (
            1 if processed['Access Road'] < 5 else 2
        )
        
        # === LOCATION STATS (from training data) ===
        # These are district-level aggregated features
        if self.location_stats is not None and district in self.location_stats:
            stats = self.location_stats[district]
            processed['new_district_area_mean'] = stats.get('area_mean', 70)
            processed['new_district_area_median'] = stats.get('area_median', 65)
            processed['new_district_area_std'] = stats.get('area_std', 30)
            processed['new_district_sample_count'] = stats.get('sample_count', 100)
            processed['new_district_tier'] = stats.get('tier', 2)
        else:
            # Use default values (roughly median values from training data)
            processed['new_district_area_mean'] = 70.0
            processed['new_district_area_median'] = 65.0
            processed['new_district_area_std'] = 30.0
            processed['new_district_sample_count'] = 100
            processed['new_district_tier'] = 2  # Middle tier
        
        # === CREATE DATAFRAME ===
        # Ensure all expected features are present in correct order
        result = {}
        for feature in EXPECTED_FEATURES:
            if feature in processed:
                result[feature] = processed[feature]
            else:
                logger.warning(f"Missing feature: {feature}, using default 0")
                result[feature] = 0
        
        df = pd.DataFrame([result])
        
        # Ensure correct order
        df = df[EXPECTED_FEATURES]
        
        logger.info(f"Preprocessed input to {len(df.columns)} features")
        
        return df

    def _to_float(self, value: Any, default: float = 0.0) -> float:
        """Convert value to float"""
        if value is None or value == '':
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def _normalize_city(self, city: str) -> str:
        """Normalize city name to standard form"""
        if not city:
            return "Hồ Chí Minh"  # Default city
        city_lower = city.lower().strip()
        return CITY_MAPPING.get(city_lower, city)

    def _encode_direction(self, direction: Any) -> int:
        """Encode direction to numeric value"""
        if isinstance(direction, (int, float)):
            return int(direction)
        if isinstance(direction, str):
            direction_lower = direction.lower().strip()
            return DIRECTION_MAPPING.get(direction_lower, 1)  # Default to "Tây" (1)
        return 1

    def _encode_legal_status(self, status: Any) -> int:
        """Encode legal status to numeric value"""
        if isinstance(status, (int, float)):
            return int(status)
        if isinstance(status, str):
            status_lower = status.lower().strip()
            return LEGAL_STATUS_MAPPING.get(status_lower, 0)  # Default to "Sổ đỏ" (0)
        return 0

    def _encode_furniture(self, furniture: Any) -> int:
        """Encode furniture state to numeric value"""
        if isinstance(furniture, (int, float)):
            return int(furniture)
        if isinstance(furniture, str):
            furniture_lower = furniture.lower().strip()
            return FURNITURE_MAPPING.get(furniture_lower, 1)  # Default to "đầy đủ" (1)
        return 1

    def _encode_categorical(self, column: str, value: str) -> int:
        """Encode categorical value using pre-fitted label encoder or hash"""
        if column in self.label_encoders:
            le = self.label_encoders[column]
            try:
                if value in le.classes_:
                    return int(le.transform([value])[0])
                else:
                    return -1  # Unknown category (trees can handle this)
            except:
                return -1
        else:
            # Fallback: use hash
            if not value:
                return 0
            return abs(hash(value)) % 1000  # Simple hash encoding


# Singleton instance
_preprocess_service: Optional[TreePreprocessService] = None


def get_preprocess_service() -> TreePreprocessService:
    """Get or create preprocessing service singleton"""
    global _preprocess_service
    if _preprocess_service is None:
        # Try to load encoders and location stats
        base_dir = Path(__file__).parent.parent.parent
        encoders_path = base_dir / "models" / "encoders_optimized.pkl"
        location_stats_path = base_dir / "models" / "location_stats_optimized.pkl"
        
        _preprocess_service = TreePreprocessService(
            encoders_path=encoders_path,
            location_stats_path=location_stats_path
        )
    return _preprocess_service

"""
Preprocessing Service - Prepare data for model prediction
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class PreprocessService:
    """Service for preprocessing input data before prediction"""

    # District mapping (common districts in Vietnam)
    DISTRICT_MAPPING = {
        "quận 1": 0, "quan 1": 0, "q1": 0,
        "quận 2": 1, "quan 2": 1, "q2": 1,
        "quận 3": 2, "quan 3": 2, "q3": 2,
        "quận 4": 3, "quan 4": 3, "q4": 3,
        "quận 5": 4, "quan 5": 4, "q5": 4,
        "quận 6": 5, "quan 6": 5, "q6": 5,
        "quận 7": 6, "quan 7": 6, "q7": 6,
        "quận 8": 7, "quan 8": 7, "q8": 7,
        "quận 9": 8, "quan 9": 8, "q9": 8,
        "quận 10": 9, "quan 10": 9, "q10": 9,
        "quận 11": 10, "quan 11": 10, "q11": 10,
        "quận 12": 11, "quan 12": 11, "q12": 12,
        "thủ đức": 13, "thu duc": 13,
        "bình thạnh": 14, "binh thanh": 14,
        "tân bình": 15, "tan binh": 15,
        "tân phú": 16, "tan phu": 16,
        "phú nhuận": 17, "phu nhuan": 17,
        "gò vấp": 18, "go vap": 18,
        "bình tân": 19, "binh tan": 19,
    }

    # Legal status mapping
    LEGAL_STATUS_MAPPING = {
        "sổ đỏ": 2, "so do": 2,
        "sổ hồng": 1, "so hong": 1,
        "hợp đồng": 0, "hop dong": 0,
        "giấy tờ đầy đủ": 2, "giay to day du": 2,
        "chưa có sổ": 0, "chua co so": 0,
    }

    # Furniture mapping
    FURNITURE_MAPPING = {
        "cao cấp": 3, "cao cap": 3, "full": 3,
        "đầy đủ": 2, "day du": 2, "basic": 2,
        "cơ bản": 1, "co ban": 1,
        "không": 0, "khong": 0, "none": 0, "trống": 0,
    }

    # Direction mapping
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

    def __init__(self):
        """Initialize preprocessing service"""
        pass

    def preprocess(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess input data for model prediction

        Args:
            data: Raw input data dictionary

        Returns:
            Preprocessed data dictionary ready for model
        """
        processed = data.copy()

        # Ensure numeric types
        numeric_fields = [
            'Area', 'Bedrooms', 'Bathrooms', 'Floors',
            'Frontage', 'AccessRoad'
        ]

        for field in numeric_fields:
            if field in processed:
                processed[field] = self._to_numeric(processed[field])

        # Encode categorical fields
        if 'District' in processed:
            processed['District'] = self._encode_district(processed['District'])

        if 'LegalStatus' in processed:
            processed['LegalStatus'] = self._encode_legal_status(processed['LegalStatus'])

        if 'Furniture' in processed:
            processed['Furniture'] = self._encode_furniture(processed['Furniture'])

        if 'Direction' in processed:
            processed['Direction'] = self._encode_direction(processed['Direction'])

        if 'BalconyDirection' in processed:
            processed['BalconyDirection'] = self._encode_direction(processed['BalconyDirection'])

        # Fill missing values with defaults
        processed = self._fill_defaults(processed)

        logger.info(f"Preprocessed data: {processed}")

        return processed

    def _to_numeric(self, value: Any) -> float:
        """Convert value to numeric"""
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    def _encode_district(self, district: Any) -> int:
        """Encode district to numeric value"""
        if isinstance(district, (int, float)):
            return int(district)

        if isinstance(district, str):
            district_lower = district.lower().strip()
            return self.DISTRICT_MAPPING.get(district_lower, 0)

        return 0

    def _encode_legal_status(self, status: Any) -> int:
        """Encode legal status to numeric value"""
        if isinstance(status, (int, float)):
            return int(status)

        if isinstance(status, str):
            status_lower = status.lower().strip()
            return self.LEGAL_STATUS_MAPPING.get(status_lower, 0)

        return 0

    def _encode_furniture(self, furniture: Any) -> int:
        """Encode furniture to numeric value"""
        if isinstance(furniture, (int, float)):
            return int(furniture)

        if isinstance(furniture, str):
            furniture_lower = furniture.lower().strip()
            return self.FURNITURE_MAPPING.get(furniture_lower, 0)

        return 0

    def _encode_direction(self, direction: Any) -> int:
        """Encode direction to numeric value"""
        if isinstance(direction, (int, float)):
            return int(direction)

        if isinstance(direction, str):
            direction_lower = direction.lower().strip()
            return self.DIRECTION_MAPPING.get(direction_lower, 0)

        return 0

    def _fill_defaults(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fill missing values with sensible defaults

        Args:
            data: Data dictionary

        Returns:
            Data with defaults filled
        """
        defaults = {
            'Area': 80.0,
            'Bedrooms': 3.0,
            'Bathrooms': 2.0,
            'Floors': 1.0,
            'Frontage': 4.0,
            'AccessRoad': 4.0,
            'District': 0,
            'LegalStatus': 1,
            'Furniture': 1,
            'Direction': 0,
            'BalconyDirection': 0,
        }

        for key, default_value in defaults.items():
            if key not in data or data[key] is None:
                data[key] = default_value

        return data

    def validate_features(self, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate input features

        Args:
            data: Input data dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for required numeric fields
        required_numeric = ['Area']

        for field in required_numeric:
            if field not in data:
                return False, f"Missing required field: {field}"

            try:
                value = float(data[field])
                if value <= 0:
                    return False, f"{field} must be positive"
            except (ValueError, TypeError):
                return False, f"{field} must be a number"

        # Validate ranges
        if 'Area' in data and float(data['Area']) > 10000:
            return False, "Area seems too large (max 10000 m²)"

        if 'Bedrooms' in data and float(data['Bedrooms']) > 20:
            return False, "Too many bedrooms (max 20)"

        if 'Bathrooms' in data and float(data['Bathrooms']) > 20:
            return False, "Too many bathrooms (max 20)"

        return True, None


# Global preprocessing service instance
preprocess_service = PreprocessService()

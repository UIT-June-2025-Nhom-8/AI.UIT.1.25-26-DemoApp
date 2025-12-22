"""
Full Preprocessing Service - Transform raw input to 392 one-hot encoded features
Matches the preprocessing used during model training
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
import json
import logging
from pathlib import Path

from ..core.config import settings

logger = logging.getLogger(__name__)


class FullPreprocessService:
    """Service for full preprocessing matching training pipeline"""

    def __init__(self):
        """Initialize service and load feature schema from model metadata"""
        self.feature_names = []
        self.feature_categories = {}
        self._load_feature_schema()

    def _load_feature_schema(self):
        """Load feature names and categories from model metadata"""
        try:
            # Load from lightgbm metadata (our default model)
            metadata_file = settings.MODELS_DIR / "lightgbm_regressor_20251205_194841_metadata.json"

            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    self.feature_names = metadata.get('feature_names', [])

                logger.info(f"Loaded {len(self.feature_names)} feature names from model metadata")

                # Parse feature categories from feature names
                self._parse_feature_categories()
            else:
                logger.warning(f"Metadata file not found: {metadata_file}")

        except Exception as e:
            logger.error(f"Failed to load feature schema: {str(e)}")

    def _parse_feature_categories(self):
        """Parse one-hot encoded feature categories from feature names"""
        for feature_name in self.feature_names:
            if '_' in feature_name:
                # One-hot encoded feature: "Category_Value"
                parts = feature_name.split('_', 1)
                if len(parts) == 2:
                    category, value = parts
                    if category not in self.feature_categories:
                        self.feature_categories[category] = []
                    if value not in self.feature_categories[category]:
                        self.feature_categories[category].append(value)

        logger.info(f"Parsed {len(self.feature_categories)} feature categories")

    def preprocess(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        Transform raw input data to 392 one-hot encoded features

        Args:
            data: Raw input dict with basic features

        Returns:
            DataFrame with single row containing 392 features
        """
        # Initialize all features to 0
        features = {name: 0.0 for name in self.feature_names}

        # Map basic numeric features (if they exist in feature_names)
        numeric_mappings = {
            'Area': ['Area', 'new_area_log'],
            'Bedrooms': ['Bedrooms'],
            'Bathrooms': ['Bathrooms'],
            'Floors': ['Floors'],
            'Frontage': ['Frontage'],
            'AccessRoad': ['Access road width'],
        }

        for input_key, feature_keys in numeric_mappings.items():
            if input_key in data:
                value = float(data[input_key])
                for feature_key in feature_keys:
                    if feature_key in features:
                        features[feature_key] = value

        # Handle one-hot encoded categorical features
        # House direction
        if 'Direction' in data:
            direction = self._normalize_direction(data['Direction'])
            feature_name = f"House direction_{direction}"
            if feature_name in features:
                features[feature_name] = 1.0

        # Balcony direction
        if 'BalconyDirection' in data:
            direction = self._normalize_direction(data['BalconyDirection'])
            feature_name = f"Balcony direction_{direction}"
            if feature_name in features:
                features[feature_name] = 1.0

        # Legal status
        if 'LegalStatus' in data:
            status = self._normalize_legal_status(data['LegalStatus'])
            feature_name = f"Legal status_{status}"
            if feature_name in features:
                features[feature_name] = 1.0

        # Furniture
        if 'Furniture' in data:
            furniture = self._normalize_furniture(data['Furniture'])
            feature_name = f"Furniture_{furniture}"
            if feature_name in features:
                features[feature_name] = 1.0

        # Computed features
        if 'Area' in data and 'Bedrooms' in data and data['Bedrooms'] > 0:
            features['new_area_per_bedroom'] = float(data['Area']) / float(data['Bedrooms'])

        if 'Bathrooms' in data and 'Bedrooms' in data and data['Bedrooms'] > 0:
            features['new_bathroom_bedroom_ratio'] = float(data['Bathrooms']) / float(data['Bedrooms'])

        if 'Bedrooms' in data and 'Bathrooms' in data:
            features['new_total_rooms'] = float(data['Bedrooms']) + float(data['Bathrooms'])

        # Binary flags
        if 'Frontage' in data:
            features['has_frontage'] = 1.0 if float(data.get('Frontage', 0)) > 0 else 0.0

        if 'AccessRoad' in data:
            features['new_has_access_road'] = 1.0 if float(data.get('AccessRoad', 0)) > 0 else 0.0

        # Size categories
        if 'Area' in data:
            area = float(data['Area'])
            features['new_is_large_house'] = 1.0 if area > 100 else 0.0
            features['new_is_luxury'] = 1.0 if area > 200 else 0.0

        if 'Floors' in data:
            features['new_is_multi_story'] = 1.0 if float(data.get('Floors', 1)) > 1 else 0.0

        # Create DataFrame
        df = pd.DataFrame([features])

        # Ensure column order matches training data
        df = df[self.feature_names]

        logger.info(f"Preprocessed to {len(df.columns)} features")

        return df

    def _normalize_direction(self, direction: Any) -> str:
        """Normalize direction values"""
        if pd.isna(direction) or direction == '' or direction is None:
            return 'Không rõ'

        direction_str = str(direction).strip().lower()

        # Mapping table
        mapping = {
            'đông': 'Đông',
            'dong': 'Đông',
            'east': 'Đông',
            'e': 'Đông',
            'tây': 'Tây',
            'tay': 'Tây',
            'west': 'Tây',
            'w': 'Tây',
            'nam': 'Nam',
            'south': 'Nam',
            's': 'Nam',
            'bắc': 'Bắc',
            'bac': 'Bắc',
            'north': 'Bắc',
            'n': 'Bắc',
            'đông nam': 'Đông - Nam',
            'dong nam': 'Đông - Nam',
            'southeast': 'Đông - Nam',
            'đông bắc': 'Đông - Bắc',
            'dong bac': 'Đông - Bắc',
            'northeast': 'Đông - Bắc',
            'tây nam': 'Tây - Nam',
            'tay nam': 'Tây - Nam',
            'southwest': 'Tây - Nam',
            'tây bắc': 'Tây - Bắc',
            'tay bac': 'Tây - Bắc',
            'northwest': 'Tây - Bắc',
        }

        return mapping.get(direction_str, 'Không rõ')

    def _normalize_legal_status(self, status: Any) -> str:
        """Normalize legal status values"""
        if pd.isna(status) or status == '' or status is None:
            return 'Không rõ'

        status_str = str(status).strip().lower()

        mapping = {
            'sổ đỏ': 'Have certificate',
            'so do': 'Have certificate',
            'sổ hồng': 'Have certificate',
            'so hong': 'Have certificate',
            'có sổ': 'Have certificate',
            'giấy tờ đầy đủ': 'Have certificate',
        }

        return mapping.get(status_str, 'Không rõ')

    def _normalize_furniture(self, furniture: Any) -> str:
        """Normalize furniture values"""
        if pd.isna(furniture) or furniture == '' or furniture is None:
            return 'Không có nội thất'

        furniture_str = str(furniture).strip().lower()

        mapping = {
            'cao cấp': 'Nội thất cao cấp',
            'cao cap': 'Nội thất cao cấp',
            'full': 'Nội thất cao cấp',
            'đầy đủ': 'Nội thất đầy đủ',
            'day du': 'Nội thất đầy đủ',
            'cơ bản': 'Nội thất cơ bản',
            'co ban': 'Nội thất cơ bản',
            'không': 'Không có nội thất',
            'khong': 'Không có nội thất',
        }

        return mapping.get(furniture_str, 'Không rõ')


# Global instance
full_preprocess_service = FullPreprocessService()

"""
Simple prediction service for demo
Returns realistic predictions based on simple rules
"""
import numpy as np
from typing import Dict, Any


def predict_simple(features: Dict[str, Any]) -> float:
    """
    Simple prediction based on area and features

    For demo purposes - returns realistic price based on simple formula:
    Price = base_price * area_multiplier * location_multiplier * quality_multiplier
    """
    # Get features with defaults
    area = float(features.get('Area', 80))
    bedrooms = float(features.get('Bedrooms', 2))
    bathrooms = float(features.get('Bathrooms', 2))
    floors = float(features.get('Floors', 1))

    # Base price per m2 in HCMC (in VND)
    base_price_per_m2 = 50_000_000  # 50 million VND/m2

    # Area multiplier (larger houses cost more per m2)
    if area < 50:
        area_mult = 0.8
    elif area < 100:
        area_mult = 1.0
    elif area < 150:
        area_mult = 1.1
    else:
        area_mult = 1.2

    # Location multiplier (district)
    district_str = str(features.get('District', '')).lower()
    if any(d in district_str for d in ['1', '2', '3', '7', 'bình thạnh', 'binh thanh']):
        location_mult = 1.5  # Prime districts
    elif any(d in district_str for d in ['4', '5', '10', '11', 'phú nhuận', 'phu nhuan']):
        location_mult = 1.2  # Good districts
    else:
        location_mult = 1.0  # Other districts

    # Quality multiplier
    furniture_str = str(features.get('Furniture', '')).lower()
    legal_str = str(features.get('LegalStatus', '')).lower()

    quality_mult = 1.0

    if any(f in furniture_str for f in ['cao cấp', 'cao cap', 'full']):
        quality_mult *= 1.15
    elif any(f in furniture_str for f in ['đầy đủ', 'day du']):
        quality_mult *= 1.05

    if any(l in legal_str for l in ['sổ đỏ', 'so do', 'sổ hồng', 'so hong']):
        quality_mult *= 1.1

    # Calculate price
    price = area * base_price_per_m2 * area_mult * location_mult * quality_mult

    # Add some randomness for realism (+/- 10%)
    noise = np.random.uniform(0.9, 1.1)
    price = price * noise

    return price


def get_confidence(features: Dict[str, Any]) -> float:
    """Return confidence score (higher for more complete data)"""
    required_fields = ['Area', 'Bedrooms', 'Bathrooms', 'District']
    present = sum(1 for f in required_fields if f in features and features[f])

    base_confidence = 70 + (present / len(required_fields)) * 20

    return min(95, base_confidence)

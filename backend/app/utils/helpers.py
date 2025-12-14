"""
Helper utilities
"""
from typing import Union


def format_price(price: float) -> str:
    """
    Format price in Vietnamese style (billion/million VND)

    Args:
        price: Price in VND

    Returns:
        Formatted price string

    Examples:
        >>> format_price(5200000000)
        '5.2 tỷ'
        >>> format_price(950000000)
        '950 triệu'
    """
    if price >= 1_000_000_000:
        # Format as billions (tỷ)
        billions = price / 1_000_000_000
        if billions >= 10:
            return f"{billions:.1f} tỷ"
        else:
            return f"{billions:.2f} tỷ"
    elif price >= 1_000_000:
        # Format as millions (triệu)
        millions = price / 1_000_000
        return f"{millions:.0f} triệu"
    else:
        # Format with thousand separators
        return f"{price:,.0f} VND"


def parse_price_input(price_input: Union[str, float, int]) -> float:
    """
    Parse price input from various formats

    Args:
        price_input: Price as string or number

    Returns:
        Price as float in VND

    Examples:
        >>> parse_price_input("5.2 tỷ")
        5200000000.0
        >>> parse_price_input("950 triệu")
        950000000.0
    """
    if isinstance(price_input, (int, float)):
        return float(price_input)

    # String parsing
    price_str = str(price_input).lower().strip()

    # Remove common separators
    price_str = price_str.replace(',', '').replace('.', '')

    # Check for billions (tỷ/ty/b)
    if any(x in price_str for x in ['tỷ', 'ty', 'b']):
        # Extract number
        for sep in ['tỷ', 'ty', 'b']:
            price_str = price_str.replace(sep, '')
        try:
            return float(price_str.strip()) * 1_000_000_000
        except ValueError:
            pass

    # Check for millions (triệu/tr/m)
    if any(x in price_str for x in ['triệu', 'trieu', 'tr', 'm']):
        for sep in ['triệu', 'trieu', 'tr', 'm']:
            price_str = price_str.replace(sep, '')
        try:
            return float(price_str.strip()) * 1_000_000
        except ValueError:
            pass

    # Try direct conversion
    try:
        return float(price_str)
    except ValueError:
        return 0.0

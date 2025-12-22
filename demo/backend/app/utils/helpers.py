"""
Helper utilities
"""
from typing import Union


def format_price(price: float) -> str:
    """
    Format price in Vietnamese style (billion/million VND)

    NOTE: Model outputs price in BILLIONS (tỷ) - range 1-12
    This function formats the price value accordingly.

    Args:
        price: Price in BILLIONS (tỷ) - model output range: 1-12

    Returns:
        Formatted price string

    Examples:
        >>> format_price(6.55)  # 6.55 tỷ VND
        '6.55 tỷ VND'
        >>> format_price(0.95)  # 0.95 tỷ = 950 triệu
        '950 triệu VND'
    """
    # Model outputs in billions (tỷ), range 1-12
    if price >= 1:
        # Format as billions (tỷ VND)
        if price >= 10:
            return f"{price:.1f} tỷ VND"
        else:
            return f"{price:.2f} tỷ VND"
    else:
        # Convert to millions for values < 1 billion (rare but possible)
        millions = price * 1000
        return f"{millions:.0f} triệu VND"


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

"""
Core module for backend API
"""
from .config import settings
from .security import create_access_token, authenticate_user
from .auth import get_current_user, get_current_user_optional

__all__ = [
    "settings",
    "create_access_token",
    "authenticate_user",
    "get_current_user",
    "get_current_user_optional"
]

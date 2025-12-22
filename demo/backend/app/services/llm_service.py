"""
LLM Parser Service - Parse Vietnamese real estate descriptions using LLM
"""
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Add backend/libs to path to import LLMParser
# Go up 3 levels: services/ -> app/ -> backend/, then into libs/
libs_path = Path(__file__).resolve().parent.parent.parent / "libs"
sys.path.insert(0, str(libs_path))

try:
    from llm_parse import LLMParser
except ImportError:
    LLMParser = None

from ..core.config import settings


logger = logging.getLogger(__name__)


class LLMService:
    """Service for parsing real estate descriptions using LLM"""

    def __init__(self):
        """Initialize LLM service"""
        self.parser: Optional[LLMParser] = None
        self.initialized = False

    def initialize(self) -> bool:
        """
        Initialize LLM parser with HuggingFace token

        Returns:
            True if initialization successful, False otherwise
        """
        if self.initialized:
            logger.info("LLM parser already initialized")
            return True

        if LLMParser is None:
            logger.error("LLMParser not available - llm_parse module not found")
            return False

        if not settings.HUGGINGFACE_TOKEN:
            logger.warning("HuggingFace token not set - LLM parsing will not be available")
            return False

        try:
            self.parser = LLMParser(token=settings.HUGGINGFACE_TOKEN)
            self.initialized = True
            logger.info("LLM parser initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize LLM parser: {str(e)}")
            return False

    def parse(self, text: str, verbose: bool = False) -> Dict[str, Any]:
        """
        Parse real estate description text into features

        Args:
            text: Description text in Vietnamese
            verbose: Whether to print verbose output

        Returns:
            Dictionary of parsed features

        Example:
            >>> text = "Nhà 100m2, 3 phòng ngủ, 2 WC, quận 7, sổ hồng"
            >>> result = llm_service.parse(text)
            >>> # Returns: {'Area': 100, 'Bedrooms': 3, 'Bathrooms': 2, ...}
        """
        # Try to initialize if not already done
        if not self.initialized:
            self.initialize()

        # If still not initialized, return empty dict
        if not self.initialized or self.parser is None:
            logger.warning("LLM parser not available - returning empty features")
            return {}

        try:
            features = self.parser.parse(text, verbose=verbose)
            logger.info(f"Parsed features from text: {features}")
            return features
        except Exception as e:
            logger.error(f"Failed to parse text: {str(e)}")
            return {}

    def is_available(self) -> bool:
        """
        Check if LLM parsing is available

        Returns:
            True if LLM parser is initialized and ready
        """
        return self.initialized and self.parser is not None


# Global LLM service instance
llm_service = LLMService()


# Try to initialize on import (will fail gracefully if token not set)
try:
    llm_service.initialize()
except Exception as e:
    logger.warning(f"Could not initialize LLM service on import: {str(e)}")

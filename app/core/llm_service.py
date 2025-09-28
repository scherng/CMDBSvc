"""
Centralized LLM Service Manager

Provides singleton LLM instances for different use cases throughout the application.
Manages API key configuration and ensures single initialization per runtime.
"""

from llama_index.llms.openai import OpenAI
from typing import Optional
import logging
from app.config.settings import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Singleton service for managing LLM instances."""

    _instance: Optional['LLMService'] = None
    _llm: Optional[OpenAI] = None
    _api_key: Optional[str] = None

    def __new__(cls) -> 'LLMService':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the service with API key from settings or fallback."""
        # Try to get API key from settings first
        self._api_key = settings.openai_api_key
        if not settings.enable_ai_field_mapping:
            logger.info("LLM is not enabled for this run")
            return
        
        if not self._api_key:
            logger.warning("No API key available for LLM services - LLM will not be available")
            return

    def get_llm(self) -> Optional[OpenAI]:
        """Get LLM instance optimized for field mapping tasks."""
        if not settings.enable_ai_field_mapping:
            logger.info("LLM is not enabled for this run")
            return None
        
        if not self._api_key:
            logger.warning("No API key available for field mapping LLM")
            return None

        if self._llm is None:
            try:
                self._llm = OpenAI(
                    model="gpt-4",
                    temperature=0.1,  # Low temperature for consistent field mapping
                    api_key=self._api_key
                )
                logger.info("LLM object is initialized")
            except Exception as e:
                logger.error(f"Failed to initialize field mapping LLM: {e}")
                return None

        return self._llm
    

    def is_available(self) -> bool:
        """Check if LLM services are available."""
        return settings.enable_ai_field_mapping and self._api_key is not None

    def get_api_key(self) -> Optional[str]:
        """Get the configured API key."""
        return self._api_key


# Global service instance
llm_service = LLMService()
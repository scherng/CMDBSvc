from typing import Dict, Any, Literal, Tuple, Optional, List
from app.db.models import User, Application
from .llm_field_mapper import LLMFieldMapper, MappingResult
import logging

logger = logging.getLogger(__name__)


class EntityDetector:
    """
    AI-enhanced entity type detection and field normalization.
    Determines whether incoming data represents a User, Application, or Device
    and normalizes field names to canonical format.
    """

    def __init__(self, enable_llm_mapping: bool = True):
        """Initialize the entity detector with optional LLM field mapping."""
        self.llm_mapper = LLMFieldMapper() if enable_llm_mapping else None
        self.enable_llm_mapping = enable_llm_mapping
        logger.info(f"EntityDetector initialized with LLM mapping: {enable_llm_mapping}")

    async def detect_and_normalize(self, data: Dict[str, Any]) -> Tuple[str, Dict[str, Any], Optional[MappingResult]]:
        """
        Detect entity type and normalize field names using AI.

        Args:
            data: Raw input data dictionary

        Returns:
            Tuple of (entity_type, normalized_data, mapping_result)
        """
        if self.llm_mapper and self.enable_llm_mapping:
            try:
                mapping_result = await self.llm_mapper.detect_and_normalize(data)

                # Convert entity type to match existing API (users -> user, applications -> application)
                entity_type_map = {
                    "users": "user",
                    "applications": "application",
                    "devices": "device"
                }
                entity_type = entity_type_map.get(mapping_result.entity_type, mapping_result.entity_type)

                logger.info(f"LLM detection successful: {entity_type}, confidence: {mapping_result.confidence_score:.2f}")
                return entity_type, mapping_result.mapped_data, mapping_result

            except Exception as e:
                logger.error(f"LLM detection failed: {e}, falling back to heuristic detection")
                # Fall through to heuristic detection

        # Fallback to original heuristic detection
        entity_type = self.detect_entity_type(data)
        return entity_type, data, None

    @staticmethod
    def detect_entity_type(data: Dict[str, Any]) -> Literal["user", "application"]:
        """
        Detect entity type based on data fields.

        Args:
            data: Input data dictionary

        Returns:
            "user" or "application"

        Raises:
            ValueError: If entity type cannot be determined
        """

        # User-specific field indicators
        user_indicators = {"mfa_enabled", "team", "last_login", "assigned_application_ids"}

        # Application-specific field indicators
        app_indicators = {"usage_count", "integrations", "type", "user_ids", "owner"}

        # Check for user indicators
        user_matches = sum(1 for key in data.keys() if key in user_indicators)

        # Check for application indicators
        app_matches = sum(1 for key in data.keys() if key in app_indicators)

        logger.debug(f"Entity detection - User indicators: {user_matches}, App indicators: {app_matches}")

        if user_matches > app_matches:
            logger.info("Detected entity type: user")
            return "user"
        elif app_matches > user_matches:
            logger.info("Detected entity type: application")
            return "application"
        elif user_matches == app_matches == 0:
            # Fallback: check for required fields
            if "name" in data:
                # Default to user if only basic fields present
                logger.info("Detected entity type: user (fallback)")
                return "user"
            else:
                raise ValueError("Cannot determine entity type: no identifying fields found")
        else:
            # Equal matches - check for distinguishing fields
            if "owner" in data:
                logger.info("Detected entity type: application (owner field present)")
                return "application"
            else:
                logger.info("Detected entity type: user (default)")
                return "user"


    def get_mapping_confidence(self, mapping_result: Optional[MappingResult]) -> float:
        """Get the confidence score from mapping result."""
        return mapping_result.confidence_score if mapping_result else 1.0

    def get_unmapped_fields(self, mapping_result: Optional[MappingResult]) -> List[str]:
        """Get list of fields that couldn't be mapped."""
        return mapping_result.unmapped_fields if mapping_result else []

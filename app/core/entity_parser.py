from typing import Dict, Any, Literal
from app.db.models import User, Application
import logging

logger = logging.getLogger(__name__)


class EntityDetector:
    """
    Simple entity type detection based on data fields.
    Determines whether incoming data represents a User or Application.
    """

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
        user_indicators = {"mfa_status", "team", "last_login", "assigned_application_ids"}

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


    async def _ai_enhanced_detection(data: Dict[str, Any]) -> Literal["user", "application"]:
        pass

    async def _ai_enhanced_extraction(self, raw_data: Dict[str, Any], config: Dict[str, Any]) -> User | Application:
        pass

from typing import Optional, Dict, Any, Union
import logging
from app.core.entity_detector import EntityDetector
from app.db.models import User, Application, UserCreate, ApplicationCreate
from app.db.connection import get_user_repository, get_application_repository

logger = logging.getLogger(__name__)


class EntityPipeline:
    """
    Pipeline for processing incoming data and creating appropriate CMDB entities.
    Handles entity detection, validation, and creation of User or Application records.
    """

    def __init__(self):
        self.detector = EntityDetector()
        self.user_repo = get_user_repository()
        self.app_repo = get_application_repository()

    async def process(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Union[User, Application]:
        """
        Process incoming data and create appropriate entity.

        Args:
            data: Input data to process
            metadata: Optional metadata (currently unused but kept for future use)

        Returns:
            Created User or Application entity

        Raises:
            ValueError: If entity type cannot be determined or creation fails
        """
        
        logger.info(f"in Process")
        try:
            # Step 1: Detect entity type
            entity_type = self.detector.detect_entity_type(data)
            logger.info(f"Processing {entity_type} entity")

            # Step 2: Create appropriate entity
            if entity_type == "user":
                return await self._create_user(data)
            elif entity_type == "application":
                return await self._create_application(data)
            else:
                raise ValueError(f"Unsupported entity type: {entity_type}")

        except Exception as e:
            logger.error(f"Pipeline processing failed: {str(e)}")
            raise

    async def _create_user(self, data: Dict[str, Any]) -> User:
        """Create a User entity from the provided data."""
        try:
            # Validate and create user data model
            user_create = UserCreate(**data)

            # Create user in repository
            user = self.user_repo.create(user_create)

            logger.info(f"User created successfully with ci_id: {user.ci_id}")
            return user

        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise ValueError(f"User creation failed: {str(e)}")

    async def _create_application(self, data: Dict[str, Any]) -> Application:
        """Create an Application entity from the provided data."""
        try:
            # Validate and create application data model
            app_create = ApplicationCreate(**data)

            # Create application in repository
            application = self.app_repo.create(app_create)

            logger.info(f"Application created successfully with ci_id: {application.ci_id}")
            return application

        except Exception as e:
            logger.error(f"Failed to create application: {str(e)}")
            raise ValueError(f"Application creation failed: {str(e)}")

    def get_entity_by_ci_id(self, ci_id: str) -> Optional[Union[User, Application]]:
        """
        Retrieve an entity by its CI ID.

        Args:
            ci_id: Configuration Item ID

        Returns:
            User or Application entity if found, None otherwise
        """
        # Try to find as user first
        user = self.user_repo.find_by_ci_id(ci_id)
        if user:
            return user

        # Try to find as application
        application = self.app_repo.find_by_ci_id(ci_id)
        if application:
            return application

        return None
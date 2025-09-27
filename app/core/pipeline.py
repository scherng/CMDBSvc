from typing import Optional, Dict, Any, Union, List
import logging
from app.core.entity_detector import EntityDetector
from app.db.models import User, Application, UserCreate, ApplicationCreate
from app.db.connection import get_user_operator, get_application_operator

logger = logging.getLogger(__name__)


class EntityPipeline:
    """
    Pipeline for processing incoming data and creating appropriate CMDB entities.
    Handles entity detection, validation, and creation of User or Application records.
    """

    def __init__(self):
        self.detector = EntityDetector()
        self.user_repo = get_user_operator()
        self.app_repo = get_application_operator()

    async def process_single(self, data: Dict[str, Any]) -> Union[User, Application]:
        """
        Process a single data item and create appropriate entity.

        Args:
            data: Input data to process

        Returns:
            Created User or Application entity

        Raises:
            ValueError: If entity type cannot be determined or creation fails
        """

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
            logger.error(f"Pipeline processing failed for single item: {str(e)}")
            raise

    async def process(self, data: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> List[Union[User, Application]]:
        """
        Process a list of data items and create appropriate entities.
        Can handle mixed entity types in the same request.

        Args:
            data: List of input data to process
            metadata: Optional metadata (currently unused but kept for future use)

        Returns:
            List of created User or Application entities

        Raises:
            ValueError: If entity type cannot be determined or creation fails
        """

        logger.info(f"Processing {len(data)} items")
        entities = []
        errors = []

        for index, item in enumerate(data):
            try:
                entity = await self.process_single(item)
                entities.append(entity)
                logger.info(f"Successfully processed item {index + 1}/{len(data)}: {entity.ci_id}")
            except Exception as e:
                error_msg = f"Failed to process item {index + 1}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)

        if errors and not entities:
            # All items failed
            raise ValueError(f"All items failed to process: {'; '.join(errors)}")
        elif errors:
            # Some items failed - log but continue
            logger.warning(f"Partial success: {len(entities)} succeeded, {len(errors)} failed")

        return entities

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
        # TODO I think we need to add a lookup table 
        # Try to find as user first
        user = self.user_repo.find_by_ci_id(ci_id)
        if user:
            return user

        # Try to find as application
        application = self.app_repo.find_by_ci_id(ci_id)
        if application:
            return application

        return None
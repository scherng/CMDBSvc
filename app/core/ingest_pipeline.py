from typing import Optional, Dict, Any, List
import logging
from app.core.entity_parser import EntityDetector
from app.core.entity_manager import EntityManager
from app.db.models import User, Application, UserCreate, ApplicationCreate

logger = logging.getLogger(__name__)


class IngestPipeline:
    def __init__(self):
        self.detector = EntityDetector()
        self.entity_mgr = EntityManager()

    async def process_single(self, data: Dict[str, Any]) -> User | Application:
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

    async def process(self, data: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> List[User | Application]:
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
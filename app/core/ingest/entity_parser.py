from typing import Dict, Any, Literal, Tuple, Optional, List
from .field_normalizer import FieldNormalizer, MappingResult
import logging
from app.config.settings import settings
from app.core.entity_data.entity_manager import EntityManager
from app.db.models import User, Application, Device, UserCreate, ApplicationCreate, DeviceCreate, EntityType


logger = logging.getLogger(__name__)


class EntityParser:
    """
    A thin wrapper on top of the FieldNormalizer
    """

    def __init__(self):
        """Initialize the entity detector with optional LLM field mapping."""
        self.normalizer = FieldNormalizer()
        self.entity_mgr = EntityManager()
        self.enable_llm_mapping = settings.enable_ai_field_mapping
        logger.info(f"EntityDetector initialized with LLM mapping: {self.enable_llm_mapping}")

    async def detect_and_normalize(self, data: Dict[str, Any]) -> Tuple[EntityType, Dict[str, Any]]:
        """
        Detect entity type and normalize field names using AI.

        Args:
            data: Raw input data dictionary

        Returns:
            Tuple of (entity_type, normalized_data, mapping_result)
        """
        try:
            mapping_result = await self.normalizer.detect_and_normalize(data)

            # Convert entity type to match existing API (users -> user, applications -> application)
            entity_type_map = {
                "users": EntityType.USER,
                "applications": EntityType.APPLICATION,
                "devices": EntityType.DEVICE
            }
            entity_type = entity_type_map.get(mapping_result.entity_type, mapping_result.entity_type)

            logger.info(f"Parse successful: {entity_type}, confidence: {mapping_result.confidence_score:.2f}")
            return entity_type, mapping_result.mapped_data

        except Exception as e:
            logger.error(f"Parse failure: {e}, returning error")
            # Fall through to heuristic detection

        # Log field mapping information
        if mapping_result:
            confidence = self.detector.get_mapping_confidence(mapping_result)
            unmapped_fields = self.detector.get_unmapped_fields(mapping_result)
            logger.info(f"Field mapping completed - confidence: {confidence:.2f}, unmapped fields: {unmapped_fields}")

            # Log individual field mappings for debugging
            for mapping in mapping_result.mappings:
                if mapping.canonical_field and mapping.confidence >= 0.7:
                    logger.debug(f"Mapped: {mapping.original_field} -> {mapping.canonical_field} (confidence: {mapping.confidence:.2f})")
                elif mapping.canonical_field is None:
                    logger.warning(f"Could not map field: {mapping.original_field}")

        return entity_type, data

        
    async def parse(self, entity_type: EntityType, normalized_data: Dict[str, Any]) -> User | Application | Device:
            if entity_type == EntityType.USER:
                return await self._create_user(normalized_data)
            elif entity_type == EntityType.APPLICATION:
                return await self._create_application(normalized_data)
            elif entity_type == EntityType.DEVICE:
                return await self._create_device(normalized_data)
            else:
                raise ValueError(f"Unsupported entity type: {entity_type}")


    async def _create_user(self, data: Dict[str, Any]) -> User:
        try:
            # Validate and create user data model
            user_create = UserCreate(**data)

            # Create user in repository
            user = self.entity_mgr.user_op.create(user_create)

            logger.info(f"User created successfully with ci_id: {user.ci_id}")
            return user

        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise ValueError(f"User creation failed: {str(e)}")

    async def _create_application(self, data: Dict[str, Any]) -> Application:
        try:
            # Validate and create application data model
            logger.info(f"In create {data}")
            app_create = ApplicationCreate(**data)

            # Create application in repository
            application = self.entity_mgr.app_op.create(app_create)

            logger.info(f"Application created successfully with ci_id: {application.ci_id}")
            return application

        except Exception as e:
            logger.error(f"Failed to create application: {str(e)}")
            raise ValueError(f"Application creation failed: {str(e)}")
        
    async def _create_device(self, data: Dict[str, Any]) -> Device:
        try:
            # Validate and create device data model
            logger.info(f"Creating device with data: {data}")
            device_create = DeviceCreate(**data)

            # Create device in repository
            device = self.entity_mgr.device_op.create(device_create)

            logger.info(f"Device created successfully with ci_id: {device.ci_id}")
            return device

        except Exception as e:
            logger.error(f"Failed to create device: {str(e)}")
            raise ValueError(f"Device creation failed: {str(e)}")

    def get_mapping_confidence(self, mapping_result: Optional[MappingResult]) -> float:
        """Get the confidence score from mapping result."""
        return mapping_result.confidence_score if mapping_result else 1.0

    def get_unmapped_fields(self, mapping_result: Optional[MappingResult]) -> List[str]:
        """Get list of fields that couldn't be mapped."""
        return mapping_result.unmapped_fields if mapping_result else []

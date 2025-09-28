from typing import Optional, Dict, Any, List
import logging
from app.core.ingest.entity_parser import EntityParser
from app.db.models import User, Application

logger = logging.getLogger(__name__)


class IngestPipeline:
    def __init__(self):
        self.parser = EntityParser()

    async def process(self, data: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> List[User | Application]:
        logger.info(f"Processing {len(data)} items")
        entities = []
        errors = []

        for index, item in enumerate(data):
            try:
                entity = await self._process_single(item)
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


    async def _process_single(self, data: Dict[str, Any]) -> User | Application:
        try:
            # Step 1: Detect entity type and normalize fields using AI
            entity_type, normalized_data = await self.parser.detect_and_normalize(data)

            # Step 2: Create appropriate entity using normalized data
            result = await self.parser.parse(entity_type, normalized_data)
            return result
        except Exception as e:
            logger.error(f"Pipeline processing failed for single item: {str(e)}")
            raise

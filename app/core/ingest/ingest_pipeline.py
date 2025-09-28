from typing import Optional, Dict, Any, List
import logging
from app.core.ingest.entity_parser import EntityParser
from app.db.models import User, Application, Device
from app.core.schemas import ProcessingResult

logger = logging.getLogger(__name__)


class IngestPipeline:
    def __init__(self):
        self.parser = EntityParser()

    async def process(self, data: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> List[ProcessingResult]:
        logger.info(f"Processing {len(data)} items")
        results = []

        for index, item in enumerate(data):
            try:
                entity = await self._process_single(item)
                result = ProcessingResult(
                    success=True,
                    entity=entity,
                    item_index=index,
                    error_message=None,
                    error_details=None
                )
                results.append(result)
                logger.info(f"Successfully processed item {index + 1}/{len(data)}: {entity.ci_id}")
            except Exception as e:
                error_msg = f"Failed to process item {index + 1}"
                error_details = str(e)
                logger.error(f"{error_msg}: {error_details}")

                result = ProcessingResult(
                    success=False,
                    entity=None,
                    item_index=index,
                    error_message=error_msg,
                    error_details=error_details
                )
                results.append(result)

        # Log summary
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        logger.info(f"Processing complete: {len(successful)} succeeded, {len(failed)} failed")

        return results


    async def _process_single(self, data: Dict[str, Any]) -> User | Application | Device:
        try:
            # Step 1: Detect entity type and normalize fields using AI
            entity_type, normalized_data = await self.parser.detect_and_normalize(data)

            # Step 2: Create appropriate entity using normalized data
            result = await self.parser.parse(entity_type, normalized_data)
            return result
        except Exception as e:
            logger.error(f"Pipeline processing failed for single item: {str(e)}")
            raise

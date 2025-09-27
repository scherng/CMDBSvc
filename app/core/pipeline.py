from typing import Optional, Dict, Any
import logging
from app.core.data_processor import DataProcessor
from app.db.local_data_storage import LocalDataStorage, ProcessingStatus
from app.config.settings import settings

logger = logging.getLogger(__name__)


class DataPipeline:

    def __init__(self, repository: LocalDataStorage):
        self.repository = repository
        self.processor = DataProcessor(
            model_name=settings.extraction_model,
            api_key=settings.openai_api_key or settings.anthropic_api_key
        )

    async def process(self, record_id: str, config: Optional[Dict[str, Any]] = None):

        try:
            record = self.repository.get_by_id(record_id)
            if not record:
                logger.error(f"Record {record_id} not found")
                return

            self.repository.update_status(record_id, ProcessingStatus.PROCESSING)

            logger.info(f"Starting processing for record {record_id}")
            processed_data = await self.processor.process(
                data=record.original_data,
                config=config
            )

            self.repository.update_processed_data(record_id, processed_data)
            logger.info(f"Processing completed for record {record_id}")

            self.repository.update_status(record_id, ProcessingStatus.COMPLETED)
            logger.info(f"Pipeline completed successfully for record {record_id}")

        except Exception as e:
            logger.error(f"Pipeline failed for record {record_id}: {str(e)}")
            self.repository.update_status(
                record_id,
                ProcessingStatus.FAILED,
                error_message=str(e)
            )
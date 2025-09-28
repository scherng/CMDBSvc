from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from app.core.schemas import EntityIngestRequest, EntityIngestResponse, SingleEntityIngestResponse
from app.core.ingest.ingest_pipeline import IngestPipeline
from app.db.models import User, Application, Device, EntityType
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/ingest", response_model=EntityIngestResponse)
async def ingest_data(request: EntityIngestRequest):
    """
    Ingest multiple data items and create appropriate CMDB entities (User, Application, or Device).

    Can handle mixed entity types in a single request. Automatically detects entity type
    for each item based on input data fields and creates the appropriate User, Application,
    or Device entity with generated CI ID.

    - **data**: List of raw input data to ingest
    - **metadata**: Optional metadata (reserved for future use)

    Returns list of entity information including CI ID and entity type for each item.
    """
    logger.info(f"Ingesting {len(request.data)} items")
    try:
        pipeline = IngestPipeline()

        # Process all data items. Currently assume everything is on bulk.
        # This part will be the candidate for optimization with streaming
        # in the future
        processing_results = await pipeline.process(
            data=request.data,
            metadata=request.metadata
        )

        # Build response for each processing result
        results = []
        current_time = datetime.now(timezone.utc)
        successful_count = 0
        failed_count = 0

        for processing_result in processing_results:
            if processing_result.success and processing_result.entity:
                # Handle successful entity creation
                entity = processing_result.entity

                # Determine entity type
                if isinstance(entity, User):
                    entity_type = EntityType.USER
                elif isinstance(entity, Application):
                    entity_type = EntityType.APPLICATION
                elif isinstance(entity, Device):
                    entity_type = EntityType.DEVICE
                else:
                    logger.warning(f"Unknown entity type for {entity}")
                    continue

                result = SingleEntityIngestResponse(
                    ci_id=entity.ci_id,
                    entity_type=entity_type,
                    message=f"{entity_type.value.capitalize()} created successfully",
                    timestamp=current_time,
                    success=True,
                    error_details=None
                )
                successful_count += 1
            else:
                # Handle failed entity creation
                result = SingleEntityIngestResponse(
                    ci_id=None,
                    entity_type=None,
                    message=processing_result.error_message or "Processing failed",
                    timestamp=current_time,
                    success=False,
                    error_details=processing_result.error_details
                )
                failed_count += 1

            results.append(result)

        # Create summary
        summary = {
            "total_items": len(request.data),
            "successful": successful_count,
            "failed": failed_count,
            "success_rate": round((successful_count / len(request.data)) * 100, 1) if request.data else 0
        }

        # Only raise an error if ALL items failed
        if failed_count > 0 and successful_count == 0:
            raise HTTPException(
                status_code=400,
                detail=f"All {failed_count} items failed to process"
            )

        return EntityIngestResponse(results=results, summary=summary)

    except ValueError as e:
        # Handle validation or detection errors
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process data: {str(e)}"
        )
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Internal processing error: {str(e)}"
        )
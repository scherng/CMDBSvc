from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from app.core.schemas import EntityIngestRequest, EntityIngestResponse, SingleEntityIngestResponse
from app.core.pipeline import EntityPipeline
from app.db.models import User, Application
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/ingest", response_model=EntityIngestResponse)
async def ingest_data(request: EntityIngestRequest):
    """
    Ingest multiple data items and create appropriate CMDB entities (User or Application).

    Can handle mixed entity types in a single request. Automatically detects entity type
    for each item based on input data fields and creates the appropriate User or
    Application entity with generated CI ID.

    - **data**: List of raw input data to ingest
    - **metadata**: Optional metadata (reserved for future use)

    Returns list of entity information including CI ID and entity type for each item.
    """
    logger.info(f"Ingesting {len(request.data)} items")
    try:
        pipeline = EntityPipeline()

        # Process all data items. Currently assume everything is on bulk. 
        # This part will be the candidate for optimization with streaming 
        # in the future
        entities = await pipeline.process(
            data=request.data,
            metadata=request.metadata
        )

        # Build response for each entity
        results = []
        current_time = datetime.now(timezone.utc)

        for entity in entities:
            # Determine entity type and extract appropriate ID
            if isinstance(entity, User):
                entity_type = "user"
            elif isinstance(entity, Application):
                entity_type = "application"
            else:
                logger.warning(f"Unknown entity type for {entity}")
                continue

            result = SingleEntityIngestResponse(
                ci_id=entity.ci_id,
                entity_type=entity_type,
                message=f"{entity_type.capitalize()} created successfully",
                timestamp=current_time
            )
            results.append(result)

        if not results:
            raise HTTPException(
                status_code=500,
                detail="No entities were successfully created"
            )

        return EntityIngestResponse(results=results)

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
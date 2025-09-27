from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from app.core.schemas import IngestRequest, EntityIngestResponse
from app.core.pipeline import EntityPipeline
from app.db.models import User, Application
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/ingest", response_model=EntityIngestResponse)
async def ingest_data(request: IngestRequest):
    """
    Ingest data and create appropriate CMDB entity (User or Application).

    Automatically detects entity type based on input data fields and creates
    the appropriate User or Application entity with generated CI ID.

    - **data**: Raw input data to ingest
    - **metadata**: Optional metadata (reserved for future use)

    Returns entity information including CI ID and entity type.
    """
    logger.info("In ingest")
    try:
        pipeline = EntityPipeline()

        # Process data synchronously
        entity = await pipeline.process(
            data=request.data,
            metadata=request.metadata
        )

        # Determine entity type and extract appropriate ID
        if isinstance(entity, User):
            entity_type = "user"
            entity_id = entity.user_id
        elif isinstance(entity, Application):
            entity_type = "application"
            entity_id = entity.app_id
        else:
            raise HTTPException(
                status_code=500,
                detail="Unknown entity type returned from pipeline"
            )

        return EntityIngestResponse(
            ci_id=entity.ci_id,
            entity_type=entity_type,
            entity_id=entity_id,
            message=f"{entity_type.capitalize()} created successfully",
            timestamp=datetime.now(timezone.utc)
        )

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
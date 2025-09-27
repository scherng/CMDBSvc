from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from app.core.schemas import EntityResponse
from app.core.pipeline import EntityPipeline
from app.db.models import User, Application

router = APIRouter()


@router.get("/ci/{ci_id}", response_model=EntityResponse)
async def fetch_data_by_ci_id(ci_id: str):
    """
    Fetch CMDB entity details by Configuration Item ID.

    Retrieves either a User or Application entity based on the provided CI ID.
    The response includes the entity type and full entity data.

    - **ci_id**: The unique Configuration Item identifier

    Returns the complete entity record with type information.
    """

    try:
        pipeline = EntityPipeline()
        entity = pipeline.get_entity_by_ci_id(ci_id)

        if not entity:
            raise HTTPException(
                status_code=404,
                detail=f"Entity with CI ID '{ci_id}' not found"
            )

        # Determine entity type and creation timestamp
        if isinstance(entity, User):
            entity_type = "user"
            # For users, we'll use current time since we don't store created_at
            # This could be enhanced by adding created_at to User model
            created_at = datetime.now(timezone.utc)
        elif isinstance(entity, Application):
            entity_type = "application"
            created_at = datetime.now(timezone.utc)
        else:
            raise HTTPException(
                status_code=500,
                detail="Unknown entity type retrieved"
            )

        return EntityResponse(
            ci_id=entity.ci_id,
            entity_type=entity_type,
            entity_data=entity,
            created_at=created_at
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve entity: {str(e)}"
        )


# Optional: Add separate endpoints for specific entity types
@router.get("/users/{ci_id}")
async def get_user_by_ci_id(ci_id: str):
    """Get User entity by CI ID."""
    pipeline = EntityPipeline()
    user = pipeline.user_repo.find_by_ci_id(ci_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/applications/{ci_id}")
async def get_application_by_ci_id(ci_id: str):
    """Get Application entity by CI ID."""
    pipeline = EntityPipeline()
    application = pipeline.app_repo.find_by_ci_id(ci_id)

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    return application
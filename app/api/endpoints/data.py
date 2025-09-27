from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone
from typing import List
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
        elif isinstance(entity, Application):
            entity_type = "application"
        else:
            raise HTTPException(
                status_code=500,
                detail="Unknown entity type retrieved"
            )

        return EntityResponse(
            ci_id=entity.ci_id,
            entity_type=entity_type,
            entity_data=entity
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


@router.get("/users", response_model=List[User])
async def list_all_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return")
):
    """
    List all users in the CMDB.

    - **skip**: Number of users to skip (for pagination)
    - **limit**: Maximum number of users to return (1-1000)

    Returns a list of all User entities.
    """
    try:
        pipeline = EntityPipeline()
        users = pipeline.user_repo.find_all(skip=skip, limit=limit)
        return users
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve users: {str(e)}"
        )


@router.get("/apps", response_model=List[Application])
async def list_all_applications(
    skip: int = Query(0, ge=0, description="Number of applications to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of applications to return")
):
    """
    List all applications in the CMDB.

    - **skip**: Number of applications to skip (for pagination)
    - **limit**: Maximum number of applications to return (1-1000)

    Returns a list of all Application entities.
    """
    try:
        pipeline = EntityPipeline()
        applications = pipeline.app_repo.find_all(skip=skip, limit=limit)
        return applications
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve applications: {str(e)}"
        )
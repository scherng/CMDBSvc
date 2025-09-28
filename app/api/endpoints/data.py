from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.core.schemas import EntityResponse
from app.core.entity_data.entity_manager import EntityManager
from app.db.models import User, Application

router = APIRouter()


@router.get("/ci/{ci_id}", response_model=EntityResponse)
async def fetch_data_by_ci_id(ci_id: str):
    try:
        entity_mgr = EntityManager()
        entity = entity_mgr.get_entity_by_ci_id(ci_id)

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
        entity_mgr = EntityManager()
        users = entity_mgr.user_op.find_all(skip=skip, limit=limit)
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
        entity_mgr = EntityManager()
        applications = entity_mgr.app_op.find_all(skip=skip, limit=limit)
        return applications
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve applications: {str(e)}"
        )
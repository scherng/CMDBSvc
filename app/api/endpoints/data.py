from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.schemas import DataResponse
from app.db.session import get_db
from app.db.local_data_storage import LocalDataStorage, ProcessingStatus

router = APIRouter()

@router.get("/ci/{record_id}", response_model=DataResponse)
async def fetch_data_by_ci_id(
    record_id: str,
    db: Session = Depends(get_db)
):
    """
    Fetch details by ID using the /ci endpoint.

    - **record_id**: The unique identifier of the data record to retrieve

    Returns the complete data record including metadata and ingestion timestamp.
    """
    repository = LocalDataStorage(db)
    record = repository.get_by_id(record_id)

    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"Data record with ID '{record_id}' not found"
        )

    return DataResponse(
        id=record.id,
        data=record.original_data,
        extracted_data=record.extracted_data,
        normalized_data=record.normalized_data,
        metadata=record.data_metadata,
        status=ProcessingStatus(record.processing_status.value),
        ingested_at=record.created_at
    )


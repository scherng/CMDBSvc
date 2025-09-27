from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.schemas import IngestRequest, IngestResponse, ProcessingStatus
from app.db.session import get_db
from app.db.local_data_storage import LocalDataStorage
from app.core.pipeline import DataPipeline

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_data(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    
    repository = LocalDataStorage(db)
    
    record = repository.create(
        data=request.data,
        metadata=request.metadata
    )
    
    pipeline = DataPipeline(repository)
    background_tasks.add_task(
        pipeline.process,
        record_id=record.id
    )
    
    return IngestResponse(
        id=record.id,
        message="Data ingested successfully. Processing in background.",
        status=ProcessingStatus.PENDING,
        timestamp=record.created_at
    )
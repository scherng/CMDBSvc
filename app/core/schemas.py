from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List
from datetime import datetime
from enum import Enum


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class IngestRequest(BaseModel):
    data: Dict[str, Any] = Field(..., description="Raw input data to ingest")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")

class IngestResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the ingested data")
    message: str = Field(..., description="Success message")
    status: ProcessingStatus = Field(..., description="Processing status")
    timestamp: datetime = Field(..., description="Ingestion timestamp")

class DataResponse(BaseModel):
    id: str
    data: Dict[str, Any]
    processed_data: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    status: ProcessingStatus
    ingested_at: datetime
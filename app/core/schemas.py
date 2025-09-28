from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List, Union
from datetime import datetime
from app.db.models import User, Application, Device, EntityType

class EntityIngestRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="Raw input data to ingest")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")

class ProcessingResult(BaseModel):
    """Internal result class for pipeline processing."""
    success: bool
    entity: Optional[Union[User, Application, Device]] = None
    error_message: Optional[str] = None
    error_details: Optional[str] = None
    item_index: int

class SingleEntityIngestResponse(BaseModel):
    ci_id: Optional[str] = Field(None, description="Configuration Item ID (null for failures)")
    entity_type: Optional[EntityType] = Field(None, description="Type of entity created (null for failures)")
    message: str = Field(..., description="Success or error message")
    timestamp: datetime = Field(..., description="Processing timestamp")
    success: bool = Field(..., description="Whether processing was successful")
    error_details: Optional[str] = Field(None, description="Detailed error information for failures")

class EntityIngestResponse(BaseModel):
    results: List[SingleEntityIngestResponse] = Field(..., description="Response for each ingested message")
    summary: Dict[str, Any] = Field(..., description="Processing summary with success/failure counts")

class EntityResponse(BaseModel):
    entity_type: EntityType
    entity_data: User | Application | Device
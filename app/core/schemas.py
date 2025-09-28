from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List
from datetime import datetime
from app.db.models import User, Application, EntityType

class EntityIngestRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="Raw input data to ingest")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")

class SingleEntityIngestResponse(BaseModel):
    ci_id: str = Field(..., description="Configuration Item ID")
    entity_type: EntityType = Field(..., description="Type of entity created")
    message: str = Field(..., description="Success message")
    timestamp: datetime = Field(..., description="Creation timestamp")

class EntityIngestResponse(BaseModel):
    results: List[SingleEntityIngestResponse] = Field(..., description="Response for each ingested message")

class EntityResponse(BaseModel):
    entity_type: EntityType
    entity_data: User | Application
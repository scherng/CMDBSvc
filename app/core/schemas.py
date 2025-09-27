from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, Union, Literal
from datetime import datetime
from app.db.models import User, Application

class IngestRequest(BaseModel):
    data: Dict[str, Any] = Field(..., description="Raw input data to ingest")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")

class EntityIngestResponse(BaseModel):
    ci_id: str = Field(..., description="Configuration Item ID")
    entity_type: Literal["user", "application"] = Field(..., description="Type of entity created")
    entity_id: str = Field(..., description="Specific entity ID (user_id or app_id)")
    message: str = Field(..., description="Success message")
    timestamp: datetime = Field(..., description="Creation timestamp")

class EntityResponse(BaseModel):
    ci_id: str
    entity_type: Literal["user", "application"]
    entity_data: Union[User, Application]
    created_at: datetime
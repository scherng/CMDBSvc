from sqlalchemy import Column, String, JSON, DateTime, Enum, Text
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.db.session import Base
import uuid
import enum

class ProcessingStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DataRecord(Base):
    __tablename__ = "data_records"

    id = Column(String, primary_key=True, index=True)
    original_data = Column(JSON, nullable=False)
    processed_data = Column(JSON, nullable=True)
    processing_status = Column(Text, nullable=False)
    data_metadata = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LocalDataStorage:
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, data: dict, metadata: Optional[dict] = None) -> DataRecord:
        record = DataRecord(
            id=str(uuid.uuid4()),
            original_data=data,
            processed_data=data,
            data_metadata=metadata,
            processing_status=ProcessingStatus.PENDING.value,
        created_at=datetime.utcnow()
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
    
    def get_by_id(self, record_id: str) -> Optional[DataRecord]:
        return self.db.query(DataRecord).filter(DataRecord.id == record_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[DataRecord]:
        return self.db.query(DataRecord).offset(skip).limit(limit).all()
    
    def update_processed_data(self, record_id: str, processed_data: dict) -> Optional[DataRecord]:
        record = self.get_by_id(record_id)
        if record:
            record.processed_data = processed_data
            record.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(record)
        return record
    
    def update_status(self, record_id: str, status: ProcessingStatus, error_message: Optional[str] = None) -> Optional[DataRecord]:
        record = self.get_by_id(record_id)
        if record:
            record.processing_status = status.value
            record.error_message = error_message
            record.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(record)
        return record
    
    def delete(self, record_id: str) -> bool:
        record = self.get_by_id(record_id)
        if record:
            self.db.delete(record)
            self.db.commit()
            return True
        return False
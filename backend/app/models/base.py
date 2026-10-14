import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from backend.app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

class BaseModel(Base):
    """Abstract base model with UUID primary key and timestamp tracking."""
    __abstract__ = True

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)

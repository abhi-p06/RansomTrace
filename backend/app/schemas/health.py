from pydantic import BaseModel, Field
from typing import Dict

class DatabaseHealth(BaseModel):
    status: str
    dialect: str
    detail: str

class HealthResponse(BaseModel):
    project: str
    version: str
    status: str
    environment: str
    timestamp_utc: str
    database: DatabaseHealth
    modules: Dict[str, str] = Field(default_factory=dict)

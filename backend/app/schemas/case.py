from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from backend.app.models.case import CaseStatus, CaseSeverity

from backend.app.core.security import validate_case_id_format, sanitize_input_text

class CaseBase(BaseModel):
    case_id: Optional[str] = Field(None, min_length=3, max_length=50)
    title: str = Field(..., min_length=3, max_length=255)
    incident_type: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    target_label: Optional[str] = Field(None, max_length=255)
    severity: CaseSeverity = Field(default=CaseSeverity.MEDIUM)
    status: CaseStatus = Field(default=CaseStatus.OPEN)

    @field_validator("case_id")
    @classmethod
    def validate_case_id_pattern(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            clean = v.strip()
            if not validate_case_id_format(clean):
                raise ValueError("Case ID must be alphanumeric and may only contain hyphens or underscores (3-64 chars)")
            return clean
        return v

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, v: str) -> str:
        clean = sanitize_input_text(v, max_length=255)
        if not clean:
            raise ValueError("Case title cannot be empty or only whitespace")
        return clean

    @field_validator("incident_type")
    @classmethod
    def sanitize_incident_type(cls, v: str) -> str:
        return sanitize_input_text(v, max_length=100)

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return sanitize_input_text(v, max_length=2000)

    @field_validator("target_label")
    @classmethod
    def sanitize_target_label(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return sanitize_input_text(v, max_length=255)

class CaseCreate(CaseBase):
    pass

class CaseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    incident_type: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    target_label: Optional[str] = Field(None, max_length=255)
    severity: Optional[CaseSeverity] = None
    status: Optional[CaseStatus] = None

    @field_validator("title")
    @classmethod
    def sanitize_update_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            clean = sanitize_input_text(v, max_length=255)
            if not clean:
                raise ValueError("Case title cannot be empty or only whitespace")
            return clean
        return None

    @field_validator("description")
    @classmethod
    def sanitize_update_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return sanitize_input_text(v, max_length=2000)
        return None

class CaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    title: str
    incident_type: str
    description: Optional[str] = None
    target_label: Optional[str] = None
    severity: str
    status: str
    created_at: datetime
    updated_at: datetime
    wallet_count: int = 0
    evidence_count: int = 0

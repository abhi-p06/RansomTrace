import enum
from sqlalchemy import Column, String, Text, Enum
from sqlalchemy.orm import relationship, synonym
from backend.app.models.base import BaseModel

class CaseStatus(str, enum.Enum):
    OPEN = "Open"
    INVESTIGATING = "Investigating"
    CONTAINED = "Contained"
    CLOSED = "Closed"

class CaseSeverity(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class InvestigationCase(BaseModel):
    __tablename__ = "investigation_cases"

    case_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    incident_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    target_label = Column(String(255), nullable=True)
    severity = Column(String(20), default=CaseSeverity.MEDIUM.value, nullable=False)
    status = Column(String(20), default=CaseStatus.OPEN.value, nullable=False)

    # Student-friendly synonym for beginner students:
    case_name = synonym("title")

    # Relationships
    wallets = relationship("Wallet", back_populates="case", cascade="all, delete-orphan")
    evidences = relationship("Evidence", back_populates="case", cascade="all, delete-orphan")
    custody_entries = relationship("ChainOfCustodyEntry", back_populates="case", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="case", cascade="all, delete-orphan")
    ml_analyses = relationship("MLAnalysis", back_populates="case", cascade="all, delete-orphan")

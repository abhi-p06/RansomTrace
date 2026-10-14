from sqlalchemy import Column, String, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.models.base import BaseModel

class RiskAssessment(BaseModel):
    __tablename__ = "risk_assessments"

    case_id = Column(String(36), ForeignKey("investigation_cases.id", ondelete="CASCADE"), nullable=True, index=True)
    wallet_id = Column(String(36), ForeignKey("wallets.id", ondelete="SET NULL"), nullable=True, index=True)
    wallet_address = Column(String(128), index=True, nullable=True)
    risk_score = Column(Float, nullable=False)  # 0.0 - 100.0
    risk_tier = Column(String(50), nullable=False)  # LOW, ELEVATED, HIGH, CRITICAL
    heuristics_summary = Column(JSON, nullable=True)
    disclaimer = Column(Text, nullable=False)
    assessed_by = Column(String(100), default="Automated Forensics Engine", nullable=False)

    case = relationship("InvestigationCase", back_populates="risk_assessments")

class MLAnalysis(BaseModel):
    __tablename__ = "ml_analyses"

    case_id = Column(String(36), ForeignKey("investigation_cases.id", ondelete="CASCADE"), nullable=True, index=True)
    wallet_id = Column(String(36), ForeignKey("wallets.id", ondelete="SET NULL"), nullable=True, index=True)
    wallet_address = Column(String(128), index=True, nullable=True)
    model_name = Column(String(100), default="IsolationForest", nullable=False)
    model_version = Column(String(50), default="1.0.0", nullable=False)
    raw_anomaly_score = Column(Float, nullable=False)
    normalized_score = Column(Float, default=0.0, nullable=False)
    classification = Column(String(50), default="NORMAL", nullable=False)
    is_anomaly = Column(Boolean, default=False, nullable=False)
    features_used = Column(JSON, nullable=True)
    feature_contributions = Column(JSON, nullable=True)
    explanation = Column(Text, nullable=True)

    case = relationship("InvestigationCase", back_populates="ml_analyses")

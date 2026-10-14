from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict

class RuleContribution(BaseModel):
    rule_id: str
    rule_name: str
    category: str
    score_contribution: float
    max_score: float
    triggered: bool
    observed_value: Any
    threshold: Any
    description: str

class MLContribution(BaseModel):
    available: bool
    raw_anomaly_score: Optional[float] = None
    normalized_score: Optional[float] = None
    classification: Optional[str] = None
    is_anomaly: Optional[bool] = None
    weight: float

class RiskWeights(BaseModel):
    rule_weight: float
    ml_weight: float

class RiskAssessmentRequest(BaseModel):
    case_id: Optional[str] = None
    wallet_address: Optional[str] = None
    include_ml: bool = True

class SimpleRiskScoreResponse(BaseModel):
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Investigative risk score (0-100)")
    risk_level: str = Field(..., description="LOW, MEDIUM, HIGH, or CRITICAL")
    risk_factors: List[str] = Field(default_factory=list, description="Observable risk factors")
    disclaimer: str = Field(..., description="Investigative disclaimer")

class RiskAssessmentResponse(BaseModel):
    id: str
    wallet_address: str
    case_id: Optional[str] = None
    final_score: float = Field(..., ge=0.0, le=100.0, description="Investigative risk score between 0.0 and 100.0")
    risk_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Investigative risk score (0-100)")
    risk_level: str = Field(..., description="LOW (0-29), MEDIUM (30-59), HIGH (60-79), or CRITICAL (80-100)")
    risk_factors: List[str] = Field(default_factory=list, description="Investigative risk factors")
    rule_score: float = Field(..., ge=0.0, le=100.0, description="Score component derived from transparent behavioral rules")
    ml_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Score component derived from ML anomaly score")
    weights: RiskWeights
    rule_contributions: List[RuleContribution]
    ml_contribution: MLContribution
    reasons: List[str]
    disclaimer: str
    assessed_by: str
    assessed_at: datetime
    data_source: str = "Public Bitcoin Blockchain & Transparent Forensics"

class RiskAssessmentHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    wallet_address: Optional[str] = None
    case_id: Optional[str] = None
    risk_score: float
    risk_tier: str
    heuristics_summary: Optional[Dict[str, Any]] = None
    disclaimer: str
    assessed_by: str
    created_at: datetime

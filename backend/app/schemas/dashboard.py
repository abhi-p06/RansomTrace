from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class RiskDistribution(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    low: int = 0
    medium: int = 0
    high: int = 0
    critical: int = 0


class RecentCaseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    title: str
    incident_type: str
    target_label: Optional[str] = None
    severity: str
    status: str
    created_at: datetime
    updated_at: datetime


class RecentEvidenceItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    artifact_type: str
    wallet_address: Optional[str] = None
    transaction_hash: Optional[str] = None
    amount_btc: Optional[float] = None
    description: Optional[str] = None
    sha256_hash: str
    captured_by: str
    seized_at: datetime


class RecentAnomalyItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: Optional[str] = None
    wallet_address: Optional[str] = None
    raw_anomaly_score: float
    normalized_score: float
    classification: str
    is_anomaly: bool
    explanation: Optional[str] = None
    created_at: datetime


class TimelineEventItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: str
    event_type: str  # CASE_CREATED, EVIDENCE_PRESERVED, CUSTODY_TRANSFER, RISK_EVALUATED, REPORT_GENERATED
    title: str
    description: str
    timestamp: datetime
    severity: Optional[str] = None
    reference_id: Optional[str] = None


class RecentTransactionItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tx_hash: str
    wallet_address: Optional[str] = None
    amount_btc: float
    direction: str  # INCOMING, OUTGOING, CONSOLIDATING
    timestamp: datetime
    status: str = "CONFIRMED"


class DashboardStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    active_cases_count: int
    total_cases_count: int
    wallets_analyzed_count: int
    transactions_analyzed_count: int
    evidence_items_count: int
    high_critical_risk_cases_count: int
    risk_distribution: RiskDistribution
    recent_cases: List[RecentCaseItem]
    recent_evidence: List[RecentEvidenceItem]
    recent_anomalies: List[RecentAnomalyItem]
    recent_transactions: List[RecentTransactionItem] = []
    timeline_events: List[TimelineEventItem]
    is_empty: bool

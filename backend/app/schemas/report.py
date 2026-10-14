from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ReportPreviewCaseInfo(BaseModel):
    id: str
    case_id: str
    title: str
    incident_type: str
    description: Optional[str] = None
    target_label: Optional[str] = None
    severity: str
    status: str
    target_wallet: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ReportPreviewAnalytics(BaseModel):
    total_tx_count: int
    incoming_tx_count: int
    outgoing_tx_count: int
    total_received_btc: float
    total_sent_btc: float
    current_balance_btc: float
    avg_tx_amount_btc: float
    tx_velocity_hourly: float
    burst_count: int
    unique_counterparties_count: int

class ReportPreviewRisk(BaseModel):
    final_score: float
    risk_level: str
    rule_score: float
    ml_score: Optional[float] = None
    rule_triggers: List[str] = []

class ReportPreviewEvidenceItem(BaseModel):
    evidence_id: str
    artifact_type: str
    description: Optional[str] = None
    sha256_hash: str
    captured_by: str
    seized_at: datetime
    custody_events_count: int

class ReportPreviewResponse(BaseModel):
    case_info: ReportPreviewCaseInfo
    target_wallet: Optional[str] = None
    analytics_summary: Optional[ReportPreviewAnalytics] = None
    risk_summary: Optional[ReportPreviewRisk] = None
    ml_classification: Optional[str] = None
    evidence_items: List[ReportPreviewEvidenceItem] = []
    chain_of_custody_count: int = 0
    generated_at: datetime
    platform_version: str = "1.0.0"
    investigator_attribution: str = "RansomTrace Automated Forensics Engine"
    disclaimer: str

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict

class FeatureItem(BaseModel):
    name: str
    label: str
    value: float
    baseline_median: float
    deviation_ratio: float
    description: str

class ModelInfo(BaseModel):
    model_name: str = "IsolationForest"
    model_version: str = "1.0.0"
    algorithm_type: str = "Unsupervised Ensemble Anomaly Detection"
    n_estimators: int = 100
    contamination: float = 0.10
    random_state: int = 42
    framework: str = "scikit-learn"
    evaluation_methodology: str = (
        "Unsupervised path length isolation heuristic (c(n) average depth) calibrated "
        "against an empirical baseline corpus. Does not report synthetic accuracy."
    )

class MLAnalysisRequest(BaseModel):
    case_id: Optional[str] = None
    wallet_address: Optional[str] = None

class MLAnalysisResponse(BaseModel):
    id: str
    wallet_address: str
    case_id: Optional[str] = None
    raw_anomaly_score: float = Field(..., description="Raw decision function score from Isolation Forest (negative = anomalous)")
    normalized_score: float = Field(..., description="Normalized anomaly risk score from 0.0 (Normal) to 100.0 (High Anomaly)")
    classification: str = Field(..., description="NORMAL, LOW ANOMALY, MEDIUM ANOMALY, or HIGH ANOMALY")
    is_anomaly: bool = Field(..., description="True if IsolationForest classified as outlier (-1)")
    features_used: Dict[str, float] = Field(..., description="Raw extracted feature values")
    feature_breakdown: List[FeatureItem] = Field(..., description="Detailed feature analysis with baseline comparisons")
    explanation: str = Field(..., description="Forensic human-readable behavioral explanation")
    model_info: ModelInfo
    evaluation_notes: str
    disclaimer: str
    analysis_timestamp: datetime
    data_source: str = "Public Bitcoin Blockchain & Mempool API"

class MLAnalysisHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    wallet_address: str
    case_id: Optional[str] = None
    raw_anomaly_score: float
    normalized_score: float
    classification: str
    is_anomaly: bool
    explanation: Optional[str] = None
    created_at: datetime


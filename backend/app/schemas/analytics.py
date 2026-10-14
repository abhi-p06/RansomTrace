from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict

class TimeSeriesPoint(BaseModel):
    date: str
    timestamp: int
    incoming_sats: int
    incoming_btc: float
    outgoing_sats: int
    outgoing_btc: float
    total_btc: float
    tx_count: int

class AmountDistributionBucket(BaseModel):
    label: str
    range_btc: str
    count: int
    percentage: float

class CounterpartyMetric(BaseModel):
    address: str
    role: str  # SENDER, RECIPIENT, BOTH
    tx_count: int
    total_sats: int
    total_btc: float

class ActivityBurst(BaseModel):
    start_time_iso: str
    end_time_iso: str
    duration_minutes: float
    tx_count: int
    total_btc: float

class WalletAnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    address: str
    address_type: str
    total_tx_count: int
    incoming_tx_count: int
    outgoing_tx_count: int
    incoming_outgoing_ratio: float
    total_received_sats: int
    total_received_btc: float
    total_sent_sats: int
    total_sent_btc: float
    current_balance_sats: int
    current_balance_btc: float

    # Statistical Metrics
    avg_tx_amount_sats: int
    avg_tx_amount_btc: float
    median_tx_amount_sats: int
    median_tx_amount_btc: float
    tx_amount_std_dev_btc: float
    min_amount_btc: float
    max_amount_btc: float

    # Velocity and Temporal Metrics
    tx_frequency_per_day: float
    avg_time_between_tx_hours: float
    first_activity_iso: Optional[str] = None
    latest_activity_iso: Optional[str] = None
    active_lifespan_days: float

    # Burst & Counterparty Metrics
    burst_count: int
    activity_bursts: List[ActivityBurst] = []
    unique_counterparties_count: int
    top_counterparties: List[CounterpartyMetric] = []

    # Chart Datasets
    volume_over_time: List[TimeSeriesPoint] = []
    amount_distribution: List[AmountDistributionBucket] = []

    data_source: str = "Public Bitcoin Blockchain Ledger"

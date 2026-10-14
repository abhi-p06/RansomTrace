from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class TxIO(BaseModel):
    address: Optional[str] = None
    value_sats: int
    value_btc: float

class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    txid: str
    block_height: Optional[int] = None
    block_time: Optional[int] = None
    block_time_iso: Optional[str] = None
    confirmed: bool = False
    fee_sats: int = 0
    fee_btc: float = 0.0
    size_bytes: Optional[int] = None
    net_value_sats: int = 0
    net_value_btc: float = 0.0
    flow_direction: str  # INCOMING, OUTGOING, TRANSIT
    inputs: List[TxIO] = []
    outputs: List[TxIO] = []
    data_source: str = "Public Bitcoin Blockchain (Mempool)"

class WalletStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    address: str
    address_type: str
    total_received_sats: int
    total_received_btc: float
    total_sent_sats: int
    total_sent_btc: float
    balance_sats: int
    balance_btc: float
    tx_count: int
    first_activity_time: Optional[int] = None
    first_activity_iso: Optional[str] = None
    latest_activity_time: Optional[int] = None
    latest_activity_iso: Optional[str] = None
    incoming_tx_count: int = 0
    outgoing_tx_count: int = 0
    data_source: str = "Public Bitcoin Blockchain (Mempool API)"
    cached: bool = False

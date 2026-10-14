from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class GraphNode(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    address: str
    short_label: str
    node_type: str  # TARGET, INFLOW_SENDER, OUTFLOW_RECEIVER, TRANSIT
    tx_count: int = 0
    received_sats: int = 0
    received_btc: float = 0.0
    sent_sats: int = 0
    sent_btc: float = 0.0
    is_target: bool = False
    degree: int = 0
    depth: int = 0

class GraphEdge(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source: str
    target: str
    txid: str
    amount_sats: int
    amount_btc: float
    block_time: Optional[int] = None
    block_time_iso: Optional[str] = None
    confirmed: bool = True

class GraphMetrics(BaseModel):
    total_nodes: int
    total_edges: int
    density: float
    max_depth_reached: int
    hub_addresses: List[str] = []

class FundFlowGraphResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    target_address: str
    depth_requested: int
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    metrics: GraphMetrics
    data_source: str = "Public Bitcoin Blockchain Ledger"

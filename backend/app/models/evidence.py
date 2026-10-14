from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.models.base import BaseModel, get_utc_now

class Evidence(BaseModel):
    __tablename__ = "evidences"

    case_id = Column(String(36), ForeignKey("investigation_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    artifact_type = Column(String(50), nullable=False)  # TRANSACTION_SNAPSHOT, WALLET_FINDING, GRAPH_CLUSTER, ML_ANOMALY_RECORD
    wallet_address = Column(String(128), index=True, nullable=True)
    transaction_hash = Column(String(128), index=True, nullable=True)
    amount_btc = Column(Float, nullable=True)
    source = Column(String(100), default="Public Bitcoin Blockchain / Mempool API", nullable=False)
    description = Column(Text, nullable=True)
    file_name = Column(String(255), nullable=True)
    file_path = Column(String(512), nullable=True)
    sha256_hash = Column(String(64), index=True, nullable=False)
    captured_by = Column(String(100), nullable=False)
    raw_payload = Column(JSON, nullable=True)
    seized_at = Column(DateTime, default=get_utc_now, nullable=False)

    case = relationship("InvestigationCase", back_populates="evidences")
    custody_entries = relationship("ChainOfCustodyEntry", back_populates="evidence", cascade="all, delete-orphan")

    # Student-friendly property aliases
    @property
    def evidence_id(self) -> str:
        return self.id

    @property
    def transaction_id(self) -> str:
        return self.transaction_hash or ""

    @property
    def amount(self) -> float:
        return self.amount_btc if self.amount_btc is not None else 0.0

    @property
    def collected_at(self) -> str:
        return self.seized_at.isoformat() if self.seized_at else ""


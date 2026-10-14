from sqlalchemy import Column, String, BigInteger, Integer, ForeignKey
from sqlalchemy.orm import relationship, synonym
from backend.app.models.base import BaseModel

class Wallet(BaseModel):
    __tablename__ = "wallets"

    case_id = Column(String(36), ForeignKey("investigation_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    address = Column(String(128), index=True, nullable=False)
    label = Column(String(255), nullable=True)
    wallet_type = Column(String(50), nullable=True)
    balance_sats = Column(BigInteger, default=0, nullable=False)
    total_received_sats = Column(BigInteger, default=0, nullable=False)
    total_sent_sats = Column(BigInteger, default=0, nullable=False)
    tx_count = Column(Integer, default=0, nullable=False)
    first_seen_timestamp = Column(BigInteger, nullable=True)
    last_seen_timestamp = Column(BigInteger, nullable=True)

    # Student-friendly synonym for beginner students:
    wallet_address = synonym("address")

    # Relationships
    case = relationship("InvestigationCase", back_populates="wallets")
    transactions = relationship("Transaction", back_populates="wallet", cascade="all, delete-orphan")
    relations = relationship("WalletRelation", back_populates="source_wallet", cascade="all, delete-orphan")

class WalletRelation(BaseModel):
    __tablename__ = "wallet_relations"

    source_wallet_id = Column(String(36), ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False, index=True)
    target_address = Column(String(128), index=True, nullable=False)
    txid = Column(String(64), index=True, nullable=False)
    value_sats = Column(BigInteger, nullable=False)
    relation_type = Column(String(50), default="HOP", nullable=False)

    source_wallet = relationship("Wallet", back_populates="relations")

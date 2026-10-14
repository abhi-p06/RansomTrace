from sqlalchemy import Column, String, BigInteger, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship, synonym
from backend.app.models.base import BaseModel

class Transaction(BaseModel):
    __tablename__ = "transactions"

    wallet_id = Column(String(36), ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False, index=True)
    txid = Column(String(64), index=True, nullable=False)
    wallet_address_val = Column("wallet_address", String(128), index=True, nullable=True)
    sender_val = Column("sender", String(128), nullable=True)
    receiver_val = Column("receiver", String(128), nullable=True)
    amount_btc = Column("amount", Float, default=0.0, nullable=True)
    block_height = Column(Integer, nullable=True)
    block_time = Column(BigInteger, nullable=True)
    fee_sats = Column(BigInteger, default=0, nullable=False)
    size_bytes = Column(Integer, nullable=True)
    net_value_sats = Column(BigInteger, default=0, nullable=False)
    flow_direction = Column(String(20), default="INCOMING", nullable=False)
    raw_inputs = Column(JSON, nullable=True)
    raw_outputs = Column(JSON, nullable=True)

    # Student-friendly synonyms for beginner students:
    transaction_id = synonym("txid")
    wallet_address = synonym("wallet_address_val")
    sender = synonym("sender_val")
    receiver = synonym("receiver_val")
    amount = synonym("amount_btc")
    timestamp = synonym("block_time")
    direction = synonym("flow_direction")

    wallet = relationship("Wallet", back_populates="transactions")

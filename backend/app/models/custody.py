from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.models.base import BaseModel, get_utc_now

class ChainOfCustodyEntry(BaseModel):
    __tablename__ = "chain_of_custody_entries"

    case_id = Column(String(36), ForeignKey("investigation_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_id = Column(String(36), ForeignKey("evidences.id", ondelete="SET NULL"), nullable=True, index=True)
    action_performed = Column(String(100), nullable=False)
    actor_name = Column(String(100), nullable=False)
    notes = Column(Text, nullable=True)
    previous_hash = Column(String(64), nullable=True)
    current_hash = Column(String(64), nullable=False)
    timestamp = Column(DateTime, default=get_utc_now, nullable=False)

    case = relationship("InvestigationCase", back_populates="custody_entries")
    evidence = relationship("Evidence", back_populates="custody_entries")

    @property
    def action(self) -> str:
        return self.action_performed

    @property
    def actor(self) -> str:
        return self.actor_name

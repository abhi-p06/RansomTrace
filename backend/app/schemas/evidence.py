from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from backend.app.core.security import (
    validate_wallet_address_format,
    validate_tx_hash_format,
    sanitize_input_text,
)

VALID_ARTIFACT_TYPES = {
    "TRANSACTION_SNAPSHOT",
    "WALLET_FINDING",
    "GRAPH_CLUSTER",
    "ML_ANOMALY_RECORD",
    "RISK_REPORT",
    "REPORT",
    "INVESTIGATIVE_NOTE",
}

CUSTODY_DISCLAIMER = (
    "This is an academic demonstration of chain-of-custody principles and does not replace formal legal evidence procedures."
)

VALID_CUSTODY_ACTIONS = {
    "COLLECTED",
    "HASHED",
    "STORED",
    "REVIEWED",
    "VERIFIED",
    "EXPORTED",
    "INTEGRITY_CHECK",
    "TRANSFERRED",
}

class SimpleCustodyRecord(BaseModel):
    id: Optional[str] = None
    evidence_id: str
    action: str
    timestamp: datetime
    actor: str
    notes: Optional[str] = None
    disclaimer: str = CUSTODY_DISCLAIMER

class ChainOfCustodyCreate(BaseModel):
    action_performed: Optional[str] = Field(None, description="COLLECTED, HASHED, STORED, REVIEWED, VERIFIED, or EXPORTED")
    action: Optional[str] = None
    actor_name: Optional[str] = Field(None, min_length=2, max_length=100)
    actor: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("action", "action_performed", mode="before")
    @classmethod
    def validate_action(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = v.strip().upper()
        if clean not in VALID_CUSTODY_ACTIONS:
            raise ValueError(f"Invalid custody action: {v}. Must be one of: {', '.join(sorted(VALID_CUSTODY_ACTIONS))}")
        return clean

    @field_validator("actor", "actor_name", mode="before")
    @classmethod
    def sanitize_actor(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = sanitize_input_text(v, max_length=100)
        if not clean:
            raise ValueError("Actor name cannot be empty")
        return clean

    @field_validator("notes")
    @classmethod
    def sanitize_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return sanitize_input_text(v, max_length=2000)

class ChainOfCustodyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    evidence_id: Optional[str] = None
    action_performed: str
    action: Optional[str] = None
    actor_name: str
    actor: Optional[str] = None
    notes: Optional[str] = None
    previous_hash: Optional[str] = None
    current_hash: str
    timestamp: datetime
    created_at: datetime
    disclaimer: str = CUSTODY_DISCLAIMER

class EvidenceCreate(BaseModel):
    case_id: str = Field(..., min_length=3, max_length=64, description="Foreign key to active InvestigationCase")
    artifact_type: str = Field(
        default="TRANSACTION_SNAPSHOT",
        description="TRANSACTION_SNAPSHOT, WALLET_FINDING, GRAPH_CLUSTER, or ML_ANOMALY_RECORD"
    )
    wallet_address: Optional[str] = None
    transaction_hash: Optional[str] = None
    amount_btc: Optional[float] = None
    source: str = Field(default="Public Bitcoin Blockchain / Mempool API", max_length=255)
    collector: str = Field(default="Forensic Investigator", min_length=2, max_length=100)
    description: str = Field(..., min_length=5, max_length=2000, description="Forensic investigative description of the seized artifact")
    raw_payload: Dict[str, Any] = Field(..., description="Unmodified canonical raw snapshot of the blockchain data")

    @field_validator("artifact_type")
    @classmethod
    def validate_artifact_type(cls, v: str) -> str:
        clean = v.strip().upper()
        if clean not in VALID_ARTIFACT_TYPES:
            raise ValueError(f"Invalid artifact type: {v}. Must be one of: {', '.join(sorted(VALID_ARTIFACT_TYPES))}")
        return clean

    @field_validator("wallet_address")
    @classmethod
    def validate_wallet(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            clean = v.strip()
            is_valid, _ = validate_wallet_address_format(clean)
            if not is_valid:
                raise ValueError(f"Invalid Bitcoin wallet address format: {clean}")
            return clean
        return None

    @field_validator("transaction_hash")
    @classmethod
    def validate_txid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            clean = v.strip()
            if not validate_tx_hash_format(clean):
                raise ValueError(f"Invalid transaction hash format. Must be 64 hexadecimal characters.")
            return clean.lower()
        return None

    @field_validator("collector")
    @classmethod
    def sanitize_collector(cls, v: str) -> str:
        clean = sanitize_input_text(v, max_length=100)
        if not clean:
            raise ValueError("Collector name cannot be empty")
        return clean

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: str) -> str:
        clean = sanitize_input_text(v, max_length=2000)
        if not clean:
            raise ValueError("Evidence description cannot be empty")
        return clean

class SimpleEvidenceRecord(BaseModel):
    evidence_id: str
    case_id: str
    transaction_id: str
    wallet_address: str
    amount: float
    timestamp: str
    source: str
    collected_at: str
    sha256_hash: str

class PreserveTransactionRequest(BaseModel):
    case_id: str = Field(..., description="Investigation Case ID")
    transaction_id: str = Field(..., description="Bitcoin Transaction ID (TXID)")
    wallet_address: str = Field(..., description="Target wallet address")
    amount: float = Field(0.0, description="Amount transferred in BTC")
    timestamp: Optional[str] = Field(None, description="Transaction timestamp (ISO or UNIX)")
    source: str = Field("Public Bitcoin Blockchain / Mempool API", description="Data provenance source")
    collector: str = Field("Forensic Investigator", description="Name of investigator")
    description: Optional[str] = Field("Forensic transaction artifact preserved as digital evidence.", description="Investigative notes")

class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    evidence_id: Optional[str] = None
    case_id: str
    artifact_type: str
    wallet_address: Optional[str] = None
    transaction_hash: Optional[str] = None
    transaction_id: Optional[str] = None
    amount_btc: Optional[float] = None
    amount: Optional[float] = None
    source: str
    description: Optional[str] = None
    sha256_hash: str
    captured_by: str
    raw_payload: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    collected_at: Optional[str] = None
    seized_at: datetime
    created_at: datetime
    custody_count: int = 0

class EvidenceDetailResponse(EvidenceResponse):
    custody_entries: List[ChainOfCustodyResponse] = []

class IntegrityVerificationResponse(BaseModel):
    evidence_id: str
    stored_hash: str
    computed_hash: str
    verified: bool
    tampered: bool
    status: str = Field(..., description="INTEGRITY VERIFIED or INTEGRITY CHECK FAILED")
    verification_timestamp: datetime
    message: str
    custody_entry_id: Optional[str] = None

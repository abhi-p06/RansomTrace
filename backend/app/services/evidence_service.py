"""
Digital Evidence Preservation and Cryptographic Integrity Subsystem
Designed for undergraduate cybersecurity investigations.

Implements:
1. Deterministic/canonical representation of evidence
2. SHA-256 fingerprinting using Python hashlib
3. Simple Evidence Record:
   - evidence_id
   - case_id
   - transaction_id
   - wallet_address
   - amount
   - timestamp
   - source
   - collected_at
   - sha256_hash
4. Integrity Verification:
   - "INTEGRITY VERIFIED" (if unchanged)
   - "INTEGRITY CHECK FAILED" (if modified/tampered)
5. Chain of Custody logging
"""

import json
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.models.evidence import Evidence
from backend.app.models.custody import ChainOfCustodyEntry
from backend.app.models.case import InvestigationCase
from backend.app.schemas.evidence import (
    EvidenceCreate,
    EvidenceResponse,
    EvidenceDetailResponse,
    ChainOfCustodyResponse,
    IntegrityVerificationResponse,
    SimpleEvidenceRecord,
    PreserveTransactionRequest,
    CUSTODY_DISCLAIMER,
    VALID_CUSTODY_ACTIONS,
)

STATUS_VERIFIED = "INTEGRITY VERIFIED"
STATUS_FAILED = "INTEGRITY CHECK FAILED"


# =============================================================================
# DETERMINISTIC CANONICAL REPRESENTATION & HASHLIB SHA-256
# =============================================================================
def create_canonical_representation(
    case_id: str,
    transaction_id: str,
    wallet_address: str,
    amount: Optional[float],
    timestamp: Any,
    source: str = "Public Bitcoin Blockchain / Mempool API",
) -> bytes:
    """
    Produces deterministic, canonical JSON byte representation for cryptographic hashing.
    Keys are strictly sorted, whitespace is eliminated, ensuring identical hashes for identical data.
    """
    canonical_dict = {
        "amount": round(float(amount), 8) if amount is not None else 0.0,
        "case_id": str(case_id or "").strip(),
        "source": str(source or "").strip(),
        "timestamp": str(timestamp or "").strip(),
        "transaction_id": str(transaction_id or "").strip().lower(),
        "wallet_address": str(wallet_address or "").strip(),
    }
    return json.dumps(
        canonical_dict,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str
    ).encode("utf-8")


def generate_evidence_hash(
    case_id: str,
    transaction_id: str,
    wallet_address: str,
    amount: Optional[float],
    timestamp: Any,
    source: str = "Public Bitcoin Blockchain / Mempool API",
) -> str:
    """
    Computes cryptographic SHA-256 hash using Python hashlib on canonical representation.
    """
    canonical_bytes = create_canonical_representation(
        case_id=case_id,
        transaction_id=transaction_id,
        wallet_address=wallet_address,
        amount=amount,
        timestamp=timestamp,
        source=source,
    )
    return hashlib.sha256(canonical_bytes).hexdigest()


def compute_sha256_hash(data: Any) -> str:
    """General canonical SHA-256 hashing helper."""
    if isinstance(data, bytes):
        return hashlib.sha256(data).hexdigest()
    if isinstance(data, str):
        return hashlib.sha256(data.encode("utf-8")).hexdigest()
    canonical_bytes = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str
    ).encode("utf-8")
    return hashlib.sha256(canonical_bytes).hexdigest()


def canonical_serialize(data: Any) -> bytes:
    """Serializes data into canonical deterministic JSON bytes."""
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        return data.encode("utf-8")
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str
    ).encode("utf-8")



# =============================================================================
# STANDALONE SIMPLE EVIDENCE PRESERVATION & VERIFICATION FUNCTIONS
# =============================================================================
def preserve_evidence_record(
    case_id: str,
    transaction_id: str,
    wallet_address: str,
    amount: float,
    timestamp: Any = None,
    source: str = "Public Bitcoin Blockchain / Mempool API",
    collector: str = "Forensic Investigator",
    description: Optional[str] = None,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """
    PRESERVE AS EVIDENCE:
    Creates a simple evidence record containing:
    - evidence_id
    - case_id
    - transaction_id
    - wallet_address
    - amount
    - timestamp
    - source
    - collected_at
    - sha256_hash
    """
    evidence_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    collected_at = now.isoformat()
    effective_ts = str(timestamp or collected_at)

    sha256_hash = generate_evidence_hash(
        case_id=case_id,
        transaction_id=transaction_id,
        wallet_address=wallet_address,
        amount=amount,
        timestamp=effective_ts,
        source=source,
    )

    record = {
        "evidence_id": evidence_id,
        "case_id": case_id,
        "transaction_id": transaction_id,
        "wallet_address": wallet_address,
        "amount": round(float(amount), 8) if amount is not None else 0.0,
        "timestamp": effective_ts,
        "source": source,
        "collected_at": collected_at,
        "sha256_hash": sha256_hash,
    }

    if db is not None:
        evidence_model = Evidence(
            id=evidence_id,
            case_id=case_id,
            artifact_type="TRANSACTION_SNAPSHOT",
            wallet_address=wallet_address,
            transaction_hash=transaction_id,
            amount_btc=amount,
            source=source,
            description=description or f"Preserved transaction {transaction_id}",
            file_name=f"evidence_{evidence_id[:8]}.json",
            sha256_hash=sha256_hash,
            captured_by=collector,
            raw_payload=record,
            seized_at=now,
            created_at=now,
            updated_at=now,
        )
        db.add(evidence_model)

        initial_entries = [
            ChainOfCustodyEntry(
                id=str(uuid.uuid4()),
                case_id=case_id,
                evidence_id=evidence_id,
                action_performed="COLLECTED",
                actor_name=collector,
                notes=f"Preserved transaction evidence from {source}.",
                previous_hash=None,
                current_hash=sha256_hash,
                timestamp=now,
                created_at=now,
                updated_at=now,
            ),
            ChainOfCustodyEntry(
                id=str(uuid.uuid4()),
                case_id=case_id,
                evidence_id=evidence_id,
                action_performed="HASHED",
                actor_name="Python hashlib Engine",
                notes=f"Computed canonical SHA-256 fingerprint: {sha256_hash}",
                previous_hash=None,
                current_hash=sha256_hash,
                timestamp=now,
                created_at=now,
                updated_at=now,
            ),
            ChainOfCustodyEntry(
                id=str(uuid.uuid4()),
                case_id=case_id,
                evidence_id=evidence_id,
                action_performed="STORED",
                actor_name="Evidence Vault Subsystem",
                notes="Preserved in tamper-evident digital forensics repository.",
                previous_hash=sha256_hash,
                current_hash=sha256_hash,
                timestamp=now,
                created_at=now,
                updated_at=now,
            ),
        ]
        db.add_all(initial_entries)
        db.commit()
        db.refresh(evidence_model)

    return record


def verify_evidence_hash(
    stored_hash: str,
    case_id: str,
    transaction_id: str,
    wallet_address: str,
    amount: float,
    timestamp: Any,
    source: str = "Public Bitcoin Blockchain / Mempool API",
) -> Tuple[bool, str, str]:
    """
    VERIFY INTEGRITY:
    Recalculates canonical SHA-256 hash and compares with stored hash.
    Returns:
        (is_verified, status_text, computed_hash)
        Where status_text is 'INTEGRITY VERIFIED' or 'INTEGRITY CHECK FAILED'.
    """
    computed_hash = generate_evidence_hash(
        case_id=case_id,
        transaction_id=transaction_id,
        wallet_address=wallet_address,
        amount=amount,
        timestamp=timestamp,
        source=source,
    )
    is_verified = (computed_hash == stored_hash)
    status_text = STATUS_VERIFIED if is_verified else STATUS_FAILED
    return is_verified, status_text, computed_hash


# =============================================================================
# EVIDENCE SERVICE CLASS (CONNECTS TO FASTAPI AND EXISTING UI)
# =============================================================================
class EvidenceService:
    """
    Service layer providing digital evidence preservation and integrity verification.
    """

    def create_evidence(self, db: Session, payload: EvidenceCreate) -> EvidenceDetailResponse:
        """
        PRESERVE AS EVIDENCE from UI Modal:
        1. Validates associated case
        2. Normalizes transaction fields
        3. Creates deterministic canonical representation and generates SHA-256 hash
        4. Inserts evidence record and initial custody entries
        """
        case = db.query(InvestigationCase).filter(InvestigationCase.id == payload.case_id).first()
        if not case:
            raise ValueError(f"Investigation Case '{payload.case_id}' does not exist.")

        evidence_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        collected_at = now.isoformat()

        tx_id = (
            payload.transaction_hash
            or (payload.raw_payload.get("transaction_id") if isinstance(payload.raw_payload, dict) else None)
            or (payload.raw_payload.get("txid") if isinstance(payload.raw_payload, dict) else None)
            or ""
        )
        wallet_addr = (
            payload.wallet_address
            or (payload.raw_payload.get("wallet_address") if isinstance(payload.raw_payload, dict) else None)
            or ""
        )
        amount_val = payload.amount_btc if payload.amount_btc is not None else 0.0
        timestamp_val = (
            (payload.raw_payload.get("timestamp") if isinstance(payload.raw_payload, dict) else None)
            or (payload.raw_payload.get("captured_at") if isinstance(payload.raw_payload, dict) else None)
            or collected_at
        )

        # Generate deterministic canonical SHA-256 hash
        sha256_hash = generate_evidence_hash(
            case_id=payload.case_id,
            transaction_id=tx_id,
            wallet_address=wallet_addr,
            amount=amount_val,
            timestamp=timestamp_val,
            source=payload.source,
        )

        # Prepare raw payload with canonical dictionary embedded
        raw_payload = dict(payload.raw_payload) if isinstance(payload.raw_payload, dict) else {}
        raw_payload.update({
            "evidence_id": evidence_id,
            "case_id": payload.case_id,
            "transaction_id": tx_id,
            "wallet_address": wallet_addr,
            "amount": amount_val,
            "timestamp": timestamp_val,
            "source": payload.source,
            "collected_at": collected_at,
            "sha256_hash": sha256_hash,
        })

        evidence = Evidence(
            id=evidence_id,
            case_id=payload.case_id,
            artifact_type=payload.artifact_type,
            wallet_address=wallet_addr or None,
            transaction_hash=tx_id or None,
            amount_btc=amount_val,
            source=payload.source,
            description=payload.description,
            file_name=f"evidence_{evidence_id[:8]}.json",
            sha256_hash=sha256_hash,
            captured_by=payload.collector,
            raw_payload=raw_payload,
            seized_at=now,
            created_at=now,
            updated_at=now,
        )
        db.add(evidence)
        db.flush()

        initial_entries = [
            ChainOfCustodyEntry(
                id=str(uuid.uuid4()),
                case_id=payload.case_id,
                evidence_id=evidence_id,
                action_performed="COLLECTED",
                actor_name=payload.collector,
                notes=f"Preserved evidence artifact from {payload.source}.",
                previous_hash=None,
                current_hash=sha256_hash,
                timestamp=now,
                created_at=now,
                updated_at=now,
            ),
            ChainOfCustodyEntry(
                id=str(uuid.uuid4()),
                case_id=payload.case_id,
                evidence_id=evidence_id,
                action_performed="HASHED",
                actor_name="Python hashlib Engine",
                notes=f"Generated deterministic SHA-256 fingerprint: {sha256_hash}",
                previous_hash=None,
                current_hash=sha256_hash,
                timestamp=now,
                created_at=now,
                updated_at=now,
            ),
            ChainOfCustodyEntry(
                id=str(uuid.uuid4()),
                case_id=payload.case_id,
                evidence_id=evidence_id,
                action_performed="STORED",
                actor_name="Evidence Vault Subsystem",
                notes="Preserved in digital forensics database.",
                previous_hash=sha256_hash,
                current_hash=sha256_hash,
                timestamp=now,
                created_at=now,
                updated_at=now,
            ),
        ]
        db.add_all(initial_entries)
        db.commit()
        db.refresh(evidence)

        custody_dtos = [ChainOfCustodyResponse.model_validate(e) for e in initial_entries]

        return EvidenceDetailResponse(
            id=evidence.id,
            evidence_id=evidence.id,
            case_id=evidence.case_id,
            artifact_type=evidence.artifact_type,
            wallet_address=evidence.wallet_address,
            transaction_hash=evidence.transaction_hash,
            transaction_id=evidence.transaction_hash,
            amount_btc=evidence.amount_btc,
            amount=evidence.amount_btc,
            source=evidence.source,
            description=evidence.description,
            sha256_hash=evidence.sha256_hash,
            captured_by=evidence.captured_by,
            raw_payload=evidence.raw_payload,
            timestamp=timestamp_val,
            collected_at=collected_at,
            seized_at=evidence.seized_at,
            created_at=evidence.created_at,
            custody_count=len(custody_dtos),
            custody_entries=custody_dtos,
        )

    def preserve_transaction(self, db: Session, req: PreserveTransactionRequest) -> SimpleEvidenceRecord:
        """
        PRESERVE AS EVIDENCE from a selected transaction:
        Accepts case_id, transaction_id, wallet_address, amount, timestamp.
        """
        record = preserve_evidence_record(
            case_id=req.case_id,
            transaction_id=req.transaction_id,
            wallet_address=req.wallet_address,
            amount=req.amount,
            timestamp=req.timestamp,
            source=req.source,
            collector=req.collector,
            description=req.description,
            db=db,
        )
        return SimpleEvidenceRecord(**record)

    def verify_evidence_integrity(
        self,
        db: Session,
        evidence_id: str,
        actor_name: str = "Automated Forensics Verifier",
    ) -> IntegrityVerificationResponse:
        """
        VERIFY INTEGRITY:
        Recomputes the canonical SHA-256 hash using Python hashlib.
        If unchanged: returns 'INTEGRITY VERIFIED'
        If altered: returns 'INTEGRITY CHECK FAILED'
        """
        evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
        if not evidence:
            raise ValueError(f"Evidence '{evidence_id}' does not exist.")

        # Extract values for canonical re-hashing
        tx_id = evidence.transaction_hash or ""
        wallet_addr = evidence.wallet_address or ""
        amount_val = evidence.amount_btc
        src = evidence.source

        # Extract recorded timestamp
        timestamp_val = ""
        if evidence.raw_payload and isinstance(evidence.raw_payload, dict):
            timestamp_val = (
                evidence.raw_payload.get("timestamp")
                or evidence.raw_payload.get("collected_at")
                or ""
            )

        # Re-compute hash from current data
        is_verified, status_text, computed_hash = verify_evidence_hash(
            stored_hash=evidence.sha256_hash,
            case_id=evidence.case_id,
            transaction_id=tx_id,
            wallet_address=wallet_addr,
            amount=amount_val,
            timestamp=timestamp_val,
            source=src,
        )

        now = datetime.now(timezone.utc)
        notes = (
            f"Cryptographic verification: {status_text}. Hash: {computed_hash}"
            if is_verified
            else f"Cryptographic verification: {status_text}. Stored: {evidence.sha256_hash}, Computed: {computed_hash}"
        )

        # Append custody verification entry
        custody_entry = ChainOfCustodyEntry(
            id=str(uuid.uuid4()),
            case_id=evidence.case_id,
            evidence_id=evidence.id,
            action_performed="VERIFIED",
            actor_name=actor_name,
            notes=notes,
            previous_hash=evidence.sha256_hash,
            current_hash=computed_hash,
            timestamp=now,
            created_at=now,
            updated_at=now,
        )
        db.add(custody_entry)
        db.commit()

        return IntegrityVerificationResponse(
            evidence_id=evidence.id,
            stored_hash=evidence.sha256_hash,
            computed_hash=computed_hash,
            verified=is_verified,
            tampered=not is_verified,
            status=status_text,
            verification_timestamp=now,
            message=notes,
            custody_entry_id=custody_entry.id,
        )

    def get_evidence_detail(self, db: Session, evidence_id: str) -> Optional[EvidenceDetailResponse]:
        """Retrieves evidence along with complete chronological Chain of Custody entries."""
        evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
        if not evidence:
            return None

        entries = (
            db.query(ChainOfCustodyEntry)
            .filter(ChainOfCustodyEntry.evidence_id == evidence_id)
            .order_by(ChainOfCustodyEntry.timestamp.asc())
            .all()
        )
        custody_dtos = [ChainOfCustodyResponse.model_validate(e) for e in entries]

        ts_val = (
            evidence.raw_payload.get("timestamp")
            if (evidence.raw_payload and isinstance(evidence.raw_payload, dict))
            else None
        )

        return EvidenceDetailResponse(
            id=evidence.id,
            evidence_id=evidence.id,
            case_id=evidence.case_id,
            artifact_type=evidence.artifact_type,
            wallet_address=evidence.wallet_address,
            transaction_hash=evidence.transaction_hash,
            transaction_id=evidence.transaction_hash,
            amount_btc=evidence.amount_btc,
            amount=evidence.amount_btc,
            source=evidence.source,
            description=evidence.description,
            sha256_hash=evidence.sha256_hash,
            captured_by=evidence.captured_by,
            raw_payload=evidence.raw_payload,
            timestamp=ts_val,
            collected_at=evidence.seized_at.isoformat() if evidence.seized_at else None,
            seized_at=evidence.seized_at,
            created_at=evidence.created_at,
            custody_count=len(custody_dtos),
            custody_entries=custody_dtos,
        )

    def list_evidence(
        self,
        db: Session,
        case_id: Optional[str] = None,
        artifact_type: Optional[str] = None,
        wallet_address: Optional[str] = None,
    ) -> List[EvidenceResponse]:
        """Lists preserved evidence records matching optional filter criteria."""
        query = db.query(Evidence)
        if case_id:
            query = query.filter(Evidence.case_id == case_id)
        if artifact_type:
            query = query.filter(Evidence.artifact_type == artifact_type)
        if wallet_address:
            query = query.filter(Evidence.wallet_address == wallet_address)

        evidences = query.order_by(desc(Evidence.seized_at)).all()

        results = []
        for e in evidences:
            count = db.query(ChainOfCustodyEntry).filter(ChainOfCustodyEntry.evidence_id == e.id).count()
            ts_val = (
                e.raw_payload.get("timestamp")
                if (e.raw_payload and isinstance(e.raw_payload, dict))
                else None
            )
            dto = EvidenceResponse(
                id=e.id,
                evidence_id=e.id,
                case_id=e.case_id,
                artifact_type=e.artifact_type,
                wallet_address=e.wallet_address,
                transaction_hash=e.transaction_hash,
                transaction_id=e.transaction_hash,
                amount_btc=e.amount_btc,
                amount=e.amount_btc,
                source=e.source,
                description=e.description,
                sha256_hash=e.sha256_hash,
                captured_by=e.captured_by,
                raw_payload=e.raw_payload,
                timestamp=ts_val,
                collected_at=e.seized_at.isoformat() if e.seized_at else None,
                seized_at=e.seized_at,
                created_at=e.created_at,
                custody_count=count,
            )
            results.append(dto)
        return results

    def get_custody_timeline(
        self,
        db: Session,
        evidence_id: str,
    ) -> List[ChainOfCustodyResponse]:
        """Returns the chronological Chain of Custody entries for an evidence item."""
        entries = (
            db.query(ChainOfCustodyEntry)
            .filter(ChainOfCustodyEntry.evidence_id == evidence_id)
            .order_by(ChainOfCustodyEntry.timestamp.asc())
            .all()
        )
        return [
            ChainOfCustodyResponse(
                id=e.id,
                case_id=e.case_id,
                evidence_id=e.evidence_id,
                action_performed=e.action_performed,
                action=e.action_performed,
                actor_name=e.actor_name,
                actor=e.actor_name,
                notes=e.notes,
                previous_hash=e.previous_hash,
                current_hash=e.current_hash,
                timestamp=e.timestamp,
                created_at=e.created_at,
                disclaimer=CUSTODY_DISCLAIMER,
            )
            for e in entries
        ]

    def append_custody_action(
        self,
        db: Session,
        evidence_id: str,
        action: str,
        actor: str,
        notes: Optional[str] = None,
    ) -> ChainOfCustodyResponse:
        """Appends a new chronological entry to the Chain of Custody log."""
        evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
        if not evidence:
            raise ValueError(f"Evidence '{evidence_id}' does not exist.")

        clean_action = str(action).strip().upper()
        if clean_action not in VALID_CUSTODY_ACTIONS:
            raise ValueError(f"Invalid custody action: {action}. Must be one of: {sorted(VALID_CUSTODY_ACTIONS)}")

        latest_entry = (
            db.query(ChainOfCustodyEntry)
            .filter(ChainOfCustodyEntry.evidence_id == evidence_id)
            .order_by(desc(ChainOfCustodyEntry.timestamp))
            .first()
        )
        prev_hash = latest_entry.current_hash if latest_entry else evidence.sha256_hash

        now = datetime.now(timezone.utc)
        new_entry = ChainOfCustodyEntry(
            id=str(uuid.uuid4()),
            case_id=evidence.case_id,
            evidence_id=evidence.id,
            action_performed=clean_action,
            actor_name=actor,
            notes=notes or f"Custody action {clean_action} performed.",
            previous_hash=prev_hash,
            current_hash=evidence.sha256_hash,
            timestamp=now,
            created_at=now,
            updated_at=now,
        )
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)

        return ChainOfCustodyResponse(
            id=new_entry.id,
            case_id=new_entry.case_id,
            evidence_id=new_entry.evidence_id,
            action_performed=new_entry.action_performed,
            action=new_entry.action_performed,
            actor_name=new_entry.actor_name,
            actor=new_entry.actor_name,
            notes=new_entry.notes,
            previous_hash=new_entry.previous_hash,
            current_hash=new_entry.current_hash,
            timestamp=new_entry.timestamp,
            created_at=new_entry.created_at,
            disclaimer=CUSTODY_DISCLAIMER,
        )


# Global service instance
evidence_service = EvidenceService()

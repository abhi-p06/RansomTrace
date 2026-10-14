import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.case import InvestigationCase
from backend.app.models.evidence import Evidence
from backend.app.models.custody import ChainOfCustodyEntry
from backend.app.services.evidence_service import (
    canonical_serialize,
    compute_sha256_hash,
    evidence_service,
)
from backend.app.schemas.evidence import EvidenceCreate, ChainOfCustodyCreate

client = TestClient(app)

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_case(db_session: Session):
    case_id = f"CASE-TEST-{datetime.now().timestamp()}"
    case = InvestigationCase(
        case_id=case_id,
        title="Evidence Preservation Unit Test Case",
        incident_type="Forensic Audit",
        description="Case for validating digital forensics life cycle.",
        target_label="Forensics Lab",
        severity="High",
        status="Investigating"
    )
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)
    return case

# 1. Test Deterministic Canonical Hashing
def test_canonical_serialization_and_hashing():
    # Two dicts with completely different key orderings and whitespace
    payload_a = {"z_output": 100, "a_input": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "meta": {"fee": 500, "height": 700000}}
    payload_b = {"a_input": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "meta": {"height": 700000, "fee": 500}, "z_output": 100}

    bytes_a = canonical_serialize(payload_a)
    bytes_b = canonical_serialize(payload_b)

    assert bytes_a == bytes_b
    hash_a = compute_sha256_hash(payload_a)
    hash_b = compute_sha256_hash(payload_b)
    assert hash_a == hash_b
    assert len(hash_a) == 64

# 2. Test Evidence Creation & Automatic Custody Chain
def test_evidence_creation_and_initial_custody(db_session: Session, test_case: InvestigationCase):
    payload = EvidenceCreate(
        case_id=test_case.id,
        artifact_type="TRANSACTION_SNAPSHOT",
        wallet_address="13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94",
        transaction_hash="aabbccddeeff00112233445566778899aabbccddeeff00112233445566778899",
        amount_btc=1.25,
        source="Public Bitcoin Blockchain / Mempool API",
        collector="Detective Miller",
        description="Seized transaction output from suspicious laundering cluster.",
        raw_payload={"txid": "aabbccddeeff00112233445566778899aabbccddeeff00112233445566778899", "value_sats": 125000000}
    )

    evidence = evidence_service.create_evidence(db=db_session, payload=payload)
    assert evidence.id is not None
    assert evidence.case_id == test_case.id
    assert evidence.sha256_hash == compute_sha256_hash(payload.raw_payload)
    assert evidence.custody_count == 3

    # Check that initial 3 entries are COLLECTED, HASHED, STORED in order
    actions = [e.action_performed for e in evidence.custody_entries]
    assert actions == ["COLLECTED", "HASHED", "STORED"]

# 3. Test Untouched Evidence Integrity Verification
def test_evidence_integrity_verification_passed(db_session: Session, test_case: InvestigationCase):
    payload = EvidenceCreate(
        case_id=test_case.id,
        artifact_type="WALLET_FINDING",
        wallet_address="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        source="Mempool API",
        collector="Forensic Analyst",
        description="Satoshi genesis address behavioral snapshot.",
        raw_payload={"address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "tx_count": 50, "balance": 5000000000}
    )
    evidence = evidence_service.create_evidence(db=db_session, payload=payload)

    # Verify integrity
    result = evidence_service.verify_evidence_integrity(
        db=db_session,
        evidence_id=evidence.id,
        actor_name="Integrity Auditor"
    )

    assert result.verified is True
    assert result.tampered is False
    assert result.status == "INTEGRITY VERIFIED ✓"
    assert result.stored_hash == result.computed_hash

# 4. Test Tamper Detection on Modified Evidence Record
def test_evidence_tamper_detection(db_session: Session, test_case: InvestigationCase):
    payload = EvidenceCreate(
        case_id=test_case.id,
        artifact_type="TRANSACTION_SNAPSHOT",
        wallet_address="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        transaction_hash="11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff",
        amount_btc=5.0,
        source="Public Blockchain",
        collector="Lead Investigator",
        description="Original authentic seizure.",
        raw_payload={"txid": "original", "amount": 5.0}
    )
    evidence = evidence_service.create_evidence(db=db_session, payload=payload)
    original_hash = evidence.sha256_hash

    # Maliciously or accidentally tamper with the stored raw_payload directly in DB
    record = db_session.query(Evidence).filter(Evidence.id == evidence.id).first()
    record.raw_payload = {"txid": "original", "amount": 500.0}  # Altered 5.0 -> 500.0!
    db_session.commit()

    # Run verification - MUST detect tampering!
    tamper_result = evidence_service.verify_evidence_integrity(
        db=db_session,
        evidence_id=evidence.id,
        actor_name="Audit System"
    )

    assert tamper_result.verified is False
    assert tamper_result.tampered is True
    assert tamper_result.status == "INTEGRITY COMPROMISED / TAMPERED ✗"
    assert tamper_result.stored_hash == original_hash
    assert tamper_result.computed_hash != original_hash
    assert "CRITICAL INTEGRITY FAILURE" in tamper_result.message

# 5. Test Append-Only Custody Log Actions
def test_append_custody_action(db_session: Session, test_case: InvestigationCase):
    payload = EvidenceCreate(
        case_id=test_case.id,
        artifact_type="REPORT",
        source="RansomTrace AI Engine",
        collector="Detective White",
        description="Preserved AI risk assessment output.",
        raw_payload={"score": 85.0, "tier": "CRITICAL"}
    )
    evidence = evidence_service.create_evidence(db=db_session, payload=payload)

    # Append valid action
    entry_reviewed = evidence_service.append_custody_action(
        db=db_session,
        evidence_id=evidence.id,
        action="REVIEWED",
        actor="Prosecutor Vance",
        notes="Reviewed for inclusion in Section 65B electronic evidence filing."
    )
    assert entry_reviewed.action_performed == "REVIEWED"
    assert entry_reviewed.actor_name == "Prosecutor Vance"

    # Append export action
    entry_exported = evidence_service.append_custody_action(
        db=db_session,
        evidence_id=evidence.id,
        action="EXPORTED",
        actor="Clerk of Court",
        notes="Exported encrypted evidence archive to judicial docket."
    )
    assert entry_exported.action_performed == "EXPORTED"

    # Invalid action rejected
    with pytest.raises(ValueError, match="Action 'MODIFIED' is not permitted"):
        evidence_service.append_custody_action(
            db=db_session,
            evidence_id=evidence.id,
            action="MODIFIED",
            actor="Bad Actor"
        )

# 6. Test Database Relationships and Cascade
def test_evidence_database_relationships(db_session: Session, test_case: InvestigationCase):
    payload = EvidenceCreate(
        case_id=test_case.id,
        artifact_type="WALLET_FINDING",
        source="Blockchain",
        collector="Officer Davis",
        description="Relationship validation finding.",
        raw_payload={"data": "test"}
    )
    evidence = evidence_service.create_evidence(db=db_session, payload=payload)

    # Check case back_populates
    case_in_db = db_session.query(InvestigationCase).filter(InvestigationCase.id == test_case.id).first()
    assert any(e.id == evidence.id for e in case_in_db.evidences)

    # Check custody entries count
    custody_entries = db_session.query(ChainOfCustodyEntry).filter(ChainOfCustodyEntry.evidence_id == evidence.id).all()
    assert len(custody_entries) >= 3

# 7. Test REST API Endpoints
def test_evidence_rest_api_endpoints(test_case: InvestigationCase):
    # POST /api/v1/evidence
    res_create = client.post(
        "/api/v1/evidence",
        json={
            "case_id": test_case.id,
            "artifact_type": "TRANSACTION_SNAPSHOT",
            "wallet_address": "13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94",
            "transaction_hash": "0e3e2357e806b6cdb1f70b54c3a3a17b6714ee1f0e68bebb44a74b1efd512098",
            "amount_btc": 2.5,
            "source": "Public Bitcoin Blockchain / Mempool API",
            "collector": "Agent Mulder",
            "description": "API seized transaction finding.",
            "raw_payload": {"txid": "0e3e2357e806b6cdb1f70b54c3a3a17b6714ee1f0e68bebb44a74b1efd512098", "amount": 2.5}
        }
    )
    assert res_create.status_code == 201
    ev_data = res_create.json()
    ev_id = ev_data["id"]
    assert ev_data["sha256_hash"] is not None

    # GET /api/v1/evidence
    res_list = client.get(f"/api/v1/evidence?case_id={test_case.id}")
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # GET /api/v1/evidence/{id}
    res_detail = client.get(f"/api/v1/evidence/{ev_id}")
    assert res_detail.status_code == 200
    detail_data = res_detail.json()
    assert len(detail_data["custody_entries"]) >= 3

    # POST /api/v1/evidence/{id}/verify
    res_verify = client.post(f"/api/v1/evidence/{ev_id}/verify?verifier_name=Agent%20Scully")
    assert res_verify.status_code == 200
    verify_data = res_verify.json()
    assert verify_data["verified"] is True
    assert verify_data["status"] == "INTEGRITY VERIFIED ✓"

    # POST /api/v1/evidence/{id}/custody
    res_custody = client.post(
        f"/api/v1/evidence/{ev_id}/custody",
        json={
            "action_performed": "REVIEWED",
            "actor_name": "Special Agent Skinner",
            "notes": "Reviewed evidence dossier for court presentation."
        }
    )
    assert res_custody.status_code == 201
    assert res_custody.json()["action_performed"] == "REVIEWED"

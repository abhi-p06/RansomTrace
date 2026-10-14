import pytest
import datetime
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.core.database import SessionLocal, get_db
from backend.app.models.case import InvestigationCase, CaseStatus, CaseSeverity
from backend.app.models.evidence import Evidence
from backend.app.schemas.evidence import EvidenceCreate
from backend.app.schemas.wallet import TransactionResponse, TxIO
from backend.app.services.evidence_service import evidence_service
from backend.app.services.analytics_service import analytics_service
from backend.app.services.ml_service import MLAnomalyService
from backend.app.services.report_service import forensic_report_service

client = TestClient(app)

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def empty_case(db_session: Session):
    case = InvestigationCase(
        case_id="RT-2026-EMPTY",
        title="Empty Dossier For Edge Case Testing",
        incident_type="Forensic Edge Verification",
        severity=CaseSeverity.LOW.value,
        status=CaseStatus.OPEN.value,
    )
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)
    yield case
    db_session.query(InvestigationCase).filter(InvestigationCase.id == case.id).delete()
    db_session.commit()


# ============================================================================
# 1. EDGE CASE: EMPTY CASE REPORT GENERATION & DETAILS
# ============================================================================

def test_empty_case_report_generation(db_session: Session, empty_case: InvestigationCase):
    """Verify PDF report compiles cleanly for a case with zero wallets and zero evidence."""
    pdf_bytes = forensic_report_service.generate_pdf_report(db=db_session, case_id=empty_case.id)
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")

    preview = forensic_report_service.get_report_preview_data(db=db_session, case_id=empty_case.id)
    assert preview.case_info.id == empty_case.id
    assert preview.target_wallet is None
    assert len(preview.evidence_items) == 0


# ============================================================================
# 2. EDGE CASE: DELETED / NONEXISTENT CASE REPORT
# ============================================================================

def test_nonexistent_case_report_raises_404():
    """Verify accessing reports for nonexistent case returns 404 Not Found."""
    res_preview = client.get("/api/v1/cases/NON_EXISTENT_UUID_999999/report/preview")
    assert res_preview.status_code == 404

    res_pdf = client.get("/api/v1/cases/NON_EXISTENT_UUID_999999/report/pdf")
    assert res_pdf.status_code == 404


# ============================================================================
# 3. EDGE CASE: DUPLICATE EVIDENCE HANDLING
# ============================================================================

def test_duplicate_evidence_handling(db_session: Session, empty_case: InvestigationCase):
    """Verify preserving the exact same blockchain finding twice succeeds and preserves audit trail."""
    payload = EvidenceCreate(
        case_id=empty_case.id,
        artifact_type="TRANSACTION_SNAPSHOT",
        wallet_address="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        transaction_hash="0e3e2357e806b6cdb1f70b54c3a3a17b6714ee1f0e68bebb44a74b1efd512098",
        amount_btc=50.0,
        source="Public Blockchain",
        collector="Lead Examiner",
        description="Duplicate preservation trial",
        raw_payload={"txid": "genesis", "amount": 50.0}
    )
    # First preservation
    ev1 = evidence_service.create_evidence(db=db_session, payload=payload)
    # Second preservation (should create distinct evidence ID with matching cryptographic hash)
    ev2 = evidence_service.create_evidence(db=db_session, payload=payload)

    assert ev1.id != ev2.id
    assert ev1.sha256_hash == ev2.sha256_hash
    assert ev1.case_id == ev2.case_id


# ============================================================================
# 4. EDGE CASE: MISSING TIMESTAMP (UNCONFIRMED MEMPOOL TX)
# ============================================================================

def test_unconfirmed_tx_missing_timestamp():
    """Verify analytics and ML safely handle unconfirmed transactions lacking timestamps."""
    tx = TransactionResponse(
        txid="0e3e2357e806b6cdb1f70b54c3a3a17b6714ee1f0e68bebb44a74b1efd512098",
        confirmed=False,
        fee_sats=5000,
        fee_btc=0.00005,
        block_height=None,
        block_time=None,  # Missing timestamp
        block_time_iso=None,
        size_bytes=250,
        net_value_sats=10000000,
        net_value_btc=0.1,
        flow_direction="INCOMING",
        inputs=[],
        outputs=[]
    )
    analytics = analytics_service.calculate_wallet_analytics(
        address="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        address_type="Legacy P2PKH",
        txs=[tx]
    )
    assert analytics.total_tx_count == 1
    assert analytics.total_received_btc == 0.1
    # Frequency should safely default to 0 when timestamps are missing
    assert analytics.tx_frequency_per_day == 0.0


# ============================================================================
# 5. EDGE CASE: ZERO TRANSACTION AMOUNT (OP_RETURN / DATA CARRIER)
# ============================================================================

def test_zero_amount_transaction_processing():
    """Verify handling of zero-amount data transactions."""
    now = datetime.datetime.now(datetime.timezone.utc)
    tx = TransactionResponse(
        txid="0e3e2357e806b6cdb1f70b54c3a3a17b6714ee1f0e68bebb44a74b1efd512098",
        confirmed=True,
        fee_sats=1000,
        fee_btc=0.00001,
        block_height=800000,
        block_time=int(now.timestamp()),
        block_time_iso=now.isoformat(),
        size_bytes=150,
        net_value_sats=0,
        net_value_btc=0.0,
        flow_direction="NEUTRAL",
        inputs=[],
        outputs=[]
    )
    analytics = analytics_service.calculate_wallet_analytics(
        address="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        address_type="Legacy P2PKH",
        txs=[tx]
    )
    assert analytics.total_tx_count == 1
    assert analytics.avg_tx_amount_btc == 0.0
    assert analytics.min_amount_btc == 0.0
    assert analytics.max_amount_btc == 0.0


# ============================================================================
# 6. EDGE CASE: WALLET WITH MANY TRANSACTIONS (SCALING STRESS)
# ============================================================================

def test_wallet_with_many_transactions_stress():
    """Verify statistical analytics and ML remain fast and stable over 500 transactions."""
    now = datetime.datetime.now(datetime.timezone.utc)
    base_time = int(now.timestamp()) - (500 * 3600)

    txs = []
    for i in range(500):
        t_time = base_time + (i * 3600)
        direction = "INCOMING" if i % 2 == 0 else "OUTGOING"
        amount = 0.5 + (i * 0.01)
        tx = TransactionResponse(
            txid=f"{i:064x}",
            confirmed=True,
            fee_sats=1200,
            fee_btc=0.000012,
            block_height=700000 + i,
            block_time=t_time,
            block_time_iso=datetime.datetime.fromtimestamp(t_time, datetime.timezone.utc).isoformat(),
            size_bytes=225,
            flow_direction=direction,
            net_value_sats=int(amount * 1e8),
            net_value_btc=round(amount, 8),
            inputs=[TxIO(address=f"1Source{i%5:028d}", value_sats=int(amount * 1e8), value_btc=round(amount, 8))],
            outputs=[TxIO(address=f"1Dest{i%5:030d}", value_sats=int(amount * 1e8), value_btc=round(amount, 8))]
        )
        txs.append(tx)

    analytics = analytics_service.calculate_wallet_analytics(
        address="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        address_type="Legacy P2PKH",
        txs=txs
    )
    assert analytics.total_tx_count == 500
    assert analytics.incoming_tx_count == 250
    assert analytics.outgoing_tx_count == 250
    assert analytics.unique_counterparties_count > 0
    assert analytics.tx_frequency_per_day > 0

    # Verify ML engine runs smoothly without memory exhaustion
    ml_service = MLAnomalyService(random_seed=42)
    features = ml_service.extract_features(
        address="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        txs=txs,
        analytics=analytics
    )
    assert features["transaction_count"] == 500
    assert len(features) == 12


# ============================================================================
# 7. EDGE CASE: EXTERNAL BLOCKCHAIN API UNAVAILABILITY (MOCK 502/504)
# ============================================================================

def test_external_blockchain_api_outage():
    """Verify endpoint returns safe 502 Bad Gateway when upstream Mempool API is down."""
    with patch(
        "backend.app.services.blockchain_service.blockchain_service.get_wallet_overview",
        side_effect=RuntimeError("Connection refused by upstream node")
    ):
        response = client.get("/api/v1/wallets/1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
        assert response.status_code == 502
        data = response.json()
        assert "currently unavailable" in data["detail"].lower()


# ============================================================================
# 8. EDGE CASE: MALFORMED UPSTREAM API RESPONSE
# ============================================================================

def test_malformed_upstream_api_response_handling():
    """Verify system handles unexpected / corrupted responses from external provider."""
    with patch(
        "backend.app.services.blockchain_service.blockchain_service.get_transaction_details",
        side_effect=ValueError("Corrupted transaction data payload")
    ):
        response = client.get("/api/v1/transactions/0e3e2357e806b6cdb1f70b54c3a3a17b6714ee1f0e68bebb44a74b1efd512098")
        assert response.status_code == 400
        data = response.json()
        assert "Corrupted transaction data payload" in data["detail"]

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.risk_service import RiskScoringService, DISCLAIMER_TEXT
from backend.app.schemas.wallet import TransactionResponse, TxIO

client = TestClient(app)

@pytest.fixture
def risk_service():
    return RiskScoringService(rule_weight=0.5, ml_weight=0.5)

def create_mock_tx(
    txid: str,
    direction: str,
    net_sats: int,
    timestamp: int,
    target_addr: str,
    peer_addr: str,
    is_peel: bool = False
) -> TransactionResponse:
    net_btc = net_sats / 100_000_000
    if direction == "INCOMING":
        inputs = [TxIO(address=peer_addr, value_sats=net_sats + 10000, value_btc=net_btc + 0.0001)]
        outputs = [TxIO(address=target_addr, value_sats=net_sats, value_btc=net_btc)]
    else:
        inputs = [TxIO(address=target_addr, value_sats=net_sats + 10000, value_btc=net_btc + 0.0001)]
        if is_peel:
            peel_sats = int(net_sats * 0.85)
            remainder = net_sats - peel_sats
            outputs = [
                TxIO(address=peer_addr, value_sats=peel_sats, value_btc=peel_sats / 1e8),
                TxIO(address="1MuleCashoutAddress00000000000001", value_sats=remainder, value_btc=remainder / 1e8)
            ]
        else:
            outputs = [TxIO(address=peer_addr, value_sats=net_sats, value_btc=net_btc)]

    return TransactionResponse(
        txid=txid,
        block_height=700000,
        block_time=timestamp,
        block_time_iso=f"timestamp-{timestamp}",
        confirmed=True,
        fee_sats=10000,
        fee_btc=0.0001,
        net_value_sats=net_sats,
        net_value_btc=net_btc,
        flow_direction=direction,
        inputs=inputs,
        outputs=outputs,
        data_source="TestFixture"
    )

# 1. Boundary Values Test
def test_risk_boundary_values(risk_service):
    # 0 - 29.99: LOW
    assert risk_service.determine_risk_level(0.0) == "LOW"
    assert risk_service.determine_risk_level(15.5) == "LOW"
    assert risk_service.determine_risk_level(29.0) == "LOW"
    assert risk_service.determine_risk_level(29.9) == "LOW"

    # 30 - 59.99: MEDIUM
    assert risk_service.determine_risk_level(30.0) == "MEDIUM"
    assert risk_service.determine_risk_level(45.0) == "MEDIUM"
    assert risk_service.determine_risk_level(59.0) == "MEDIUM"
    assert risk_service.determine_risk_level(59.9) == "MEDIUM"

    # 60 - 79.99: HIGH
    assert risk_service.determine_risk_level(60.0) == "HIGH"
    assert risk_service.determine_risk_level(70.5) == "HIGH"
    assert risk_service.determine_risk_level(79.0) == "HIGH"
    assert risk_service.determine_risk_level(79.9) == "HIGH"

    # 80 - 100: CRITICAL
    assert risk_service.determine_risk_level(80.0) == "CRITICAL"
    assert risk_service.determine_risk_level(95.0) == "CRITICAL"
    assert risk_service.determine_risk_level(100.0) == "CRITICAL"

# 2. Missing Transaction Features / Empty History Test
def test_risk_missing_transaction_features(risk_service):
    target = "1EmptyWalletAddress00000000000000001"
    score, contributions, reasons = risk_service.evaluate_behavioral_rules(target, [])
    assert score == 0.0
    assert len(contributions) == 7
    for c in contributions:
        assert c.triggered is False
        assert c.score_contribution == 0.0
    assert "zero observed transactions" in reasons[0]

# 3. Low-Risk Behaviour Test
def test_risk_low_behavior(risk_service):
    target = "1LowRiskPersonalWallet00000000000001"
    # Spaced out 4 transactions over a month, modest amounts, 2 counterparties, no bursts
    base_time = 1600000000
    txs = [
        create_mock_tx("tx1", "INCOMING", 2_000_000, base_time, target, "1PeerA0000000000000000000000000001"),
        create_mock_tx("tx2", "OUTGOING", 1_800_000, base_time + 86400 * 7, target, "1PeerB0000000000000000000000000001"),
        create_mock_tx("tx3", "INCOMING", 1_500_000, base_time + 86400 * 14, target, "1PeerA0000000000000000000000000001"),
        create_mock_tx("tx4", "OUTGOING", 1_400_000, base_time + 86400 * 21, target, "1PeerB0000000000000000000000000001")
    ]

    rule_score, contributions, reasons = risk_service.evaluate_behavioral_rules(target, txs)
    assert rule_score <= 25.0
    assert risk_service.determine_risk_level(rule_score) == "LOW"

# 4. Medium-Risk Behaviour Test
def test_risk_medium_behavior(risk_service):
    target = "1MediumRiskWallet00000000000000001"
    # 2 bursts within 30m (+10 pts) + 1 peeling spend (+8 pts) + 6 counterparties (+4 pts) + amount variance (+8 pts)
    base_time = 1610000000
    txs = [
        create_mock_tx("tx_0", "INCOMING", 100_000_000, base_time, target, "1PeerA0000000000000000000000000001"),
        create_mock_tx("tx_1", "OUTGOING", 10_000_000, base_time + 300, target, "1PeerB0000000000000000000000000001", is_peel=True),
        create_mock_tx("tx_2", "OUTGOING", 5_000_000, base_time + 600, target, "1PeerC0000000000000000000000000001"),
        create_mock_tx("tx_3", "INCOMING", 20_000_000, base_time + 86400, target, "1PeerD0000000000000000000000000001"),
        create_mock_tx("tx_4", "OUTGOING", 8_000_000, base_time + 86400 + 300, target, "1PeerE0000000000000000000000000001"),
        create_mock_tx("tx_5", "OUTGOING", 7_000_000, base_time + 86400 + 600, target, "1PeerF0000000000000000000000000001"),
    ]

    rule_score, contributions, reasons = risk_service.evaluate_behavioral_rules(target, txs)
    assert 25.0 <= rule_score <= 59.0

    mock_db = pytest.importorskip("unittest.mock").MagicMock()
    assessment = risk_service.assess_wallet(
        db=mock_db,
        wallet_address=target,
        txs=txs,
        include_ml=True,
        ml_score_override=45.0
    )
    assert 30.0 <= assessment.final_score <= 59.9
    assert assessment.risk_level == "MEDIUM"

# 5. High-Risk Behaviour Test
def test_risk_high_behavior(risk_service):
    target = "1HighRiskLaunderingWallet0000000001"
    # 25 rapid peeling spends with 20 counterparties and multiple bursts
    base_time = 1620000000
    txs = []
    # 1 deposit
    txs.append(create_mock_tx("dep1", "INCOMING", 100_000_000, base_time, target, "1VictimDeposit0000000000000000001"))
    # 24 rapid peel spends within 2 hours
    for i in range(1, 25):
        txs.append(create_mock_tx(
            f"peel_{i}",
            "OUTGOING",
            3_000_000,
            base_time + (i * 240),
            target,
            f"1MuleNode{i:04d}0000000000000000000001",
            is_peel=True
        ))

    rule_score, contributions, reasons = risk_service.evaluate_behavioral_rules(target, txs)
    assert rule_score >= 60.0
    tier = risk_service.determine_risk_level(rule_score)
    assert tier in ("HIGH", "CRITICAL")

# 6. Missing ML Score Test (Graceful Fallback to 100% Rules)
def test_risk_missing_ml_score(risk_service):
    target = "1FallbackRulesOnlyWallet000000000001"
    # Single mock tx
    mock_tx = create_mock_tx("tx_01", "INCOMING", 10_000_000, 1600000000, target, "1PeerA0000000000000000000000000001")

    # Mock DB session
    mock_db = pytest.importorskip("unittest.mock").MagicMock()

    # Call with include_ml=False
    assessment = risk_service.assess_wallet(
        db=mock_db,
        wallet_address=target,
        txs=[mock_tx],
        include_ml=False
    )

    assert assessment.ml_contribution.available is False
    assert assessment.weights.rule_weight == 1.0
    assert assessment.weights.ml_weight == 0.0
    assert assessment.final_score == assessment.rule_score
    assert any("ML anomaly score was not available" in r for r in assessment.reasons)
    assert assessment.disclaimer == DISCLAIMER_TEXT

# 7. Mandatory Disclaimer Presence in All Results
def test_risk_disclaimer_compliance(risk_service):
    assert "investigative indicator based on observable transaction behaviour" in DISCLAIMER_TEXT
    assert "does not establish criminal liability or identify a person" in DISCLAIMER_TEXT

    # Verify REST endpoint returns the disclaimer
    response = client.get("/api/v1/risk/rules")
    assert response.status_code == 200
    data = response.json()
    assert data["disclaimer"] == DISCLAIMER_TEXT

# 8. REST API Assessment Endpoint Test
def test_risk_assess_api_endpoint():
    test_addr = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"

    mock_tx = TransactionResponse(
        txid="00000000000000000000000000000000000000000000000000000000000000bb",
        block_height=100000,
        block_time=1600000000,
        block_time_iso="2020-09-13 12:26:40 UTC",
        confirmed=True,
        fee_sats=10000,
        fee_btc=0.0001,
        net_value_sats=50000000,
        net_value_btc=0.5,
        flow_direction="INCOMING",
        inputs=[TxIO(address="1PeerSender0000000000000000000001", value_sats=50010000, value_btc=0.5001)],
        outputs=[TxIO(address=test_addr, value_sats=50000000, value_btc=0.5)],
        data_source="Mock"
    )

    with patch("backend.app.services.blockchain_service.blockchain_service.get_wallet_transactions", new_callable=AsyncMock) as mock_get_txs:
        mock_get_txs.return_value = [mock_tx]

        response = client.post(f"/api/v1/risk/assess/{test_addr}")
        assert response.status_code == 201
        data = response.json()
        assert data["wallet_address"] == test_addr
        assert data["risk_level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
        assert 0.0 <= data["final_score"] <= 100.0
        assert data["disclaimer"] == DISCLAIMER_TEXT
        assert len(data["rule_contributions"]) == 7
        assert data["weights"]["rule_weight"] + data["weights"]["ml_weight"] == 1.0

        # History GET
        hist_res = client.get(f"/api/v1/risk/history/{test_addr}")
        assert hist_res.status_code == 200
        hist_data = hist_res.json()
        assert len(hist_data) >= 1
        assert hist_data[0]["wallet_address"] == test_addr

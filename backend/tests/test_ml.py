import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.ml_service import MLAnomalyService, FEATURE_KEYS
from backend.app.schemas.wallet import TransactionResponse, TxIO

client = TestClient(app)

@pytest.fixture
def ml_service():
    return MLAnomalyService(random_seed=42)

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
            # 2 outputs: 85% to peer change, 15% to target/service
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

# 1. Edge Case: Insufficient / Zero History
def test_ml_zero_and_single_tx(ml_service):
    target = "1TestEmptyWalletAddress00000000001"
    features_empty = ml_service.extract_features(target, [])
    assert len(features_empty) == 12
    for k in FEATURE_KEYS:
        assert features_empty[k] == 0.0

    raw, norm, classification, is_anomaly = ml_service.score_features(features_empty)
    assert classification == "NORMAL"
    assert is_anomaly is False
    assert norm <= 30.0

    # Single transaction
    tx1 = create_mock_tx("tx01", "INCOMING", 10_000_000, 1600000000, target, "1PeerA0000000000000000000000000001")
    features_single = ml_service.extract_features(target, [tx1])
    assert features_single["transaction_count"] == 1.0
    assert features_single["incoming_count"] == 1.0
    assert features_single["outgoing_count"] == 0.0

    raw_s, norm_s, classification_s, is_anomaly_s = ml_service.score_features(features_single)
    assert classification_s == "NORMAL"
    assert is_anomaly_s is False

# 2. Normal-Looking Data Test
def test_ml_normal_wallet_behavior(ml_service):
    target = "1StandardPersonalWallet0000000001"
    # 6 transactions spaced 7 days apart, modest amounts, balanced in/out
    txs = []
    base_time = 1600000000
    for i in range(3):
        txs.append(create_mock_tx(f"tx_in_{i}", "INCOMING", 5_000_000, base_time + (i * 604800), target, f"1PeerIn{i}0000000000000000000000001"))
        txs.append(create_mock_tx(f"tx_out_{i}", "OUTGOING", 4_500_000, base_time + (i * 604800) + 86400, target, f"1PeerOut{i}000000000000000000000001"))

    features = ml_service.extract_features(target, txs)
    raw, norm, classification, is_anomaly = ml_service.score_features(features)

    assert classification in ("NORMAL", "LOW ANOMALY")
    assert norm <= 55.0

    explanation, breakdown = ml_service.generate_behavioral_explanation(features, classification, norm)
    assert len(breakdown) == 12
    assert "investigative indicator and does not establish criminal activity" in explanation

# 3. Synthetic Anomalous Test Data (High Velocity + Burst + Peel Chain)
def test_ml_synthetic_anomalous_wallet(ml_service):
    target = "1SyntheticMuleLaunderingChain0001"
    # 30 transactions within 2 hours, all 2-output peel chains with rapid churn and 25 counterparties
    txs = []
    base_time = 1620000000
    for i in range(25):
        # 1 incoming deposit, followed by 24 rapid peeling transactions every 3 minutes
        if i == 0:
            txs.append(create_mock_tx(f"tx_deposit_{i}", "INCOMING", 500_000_000, base_time, target, "1VictimPayment000000000000000000001"))
        else:
            txs.append(create_mock_tx(
                f"tx_peel_{i}",
                "OUTGOING",
                20_000_000,
                base_time + (i * 180),  # 3 min intervals
                target,
                f"1CounterpartyMule{i:04d}00000000000000001",
                is_peel=True
            ))

    features = ml_service.extract_features(target, txs)
    assert features["peel_chain_indicator"] > 0.8
    assert features["activity_burst_count"] > 0
    assert features["unique_counterparties"] >= 20

    raw, norm, classification, is_anomaly = ml_service.score_features(features)
    assert classification in ("MEDIUM ANOMALY", "HIGH ANOMALY")
    assert norm >= 55.0
    assert raw < 0.0

    explanation, breakdown = ml_service.generate_behavioral_explanation(features, classification, norm)
    assert "Peel Chain Metric" in explanation or "Transaction Velocity" in explanation or "Activity Bursts" in explanation
    assert "investigative indicator and does not establish criminal activity" in explanation

# 4. Reproducibility Test
def test_ml_reproducibility():
    service_a = MLAnomalyService(random_seed=42)
    service_b = MLAnomalyService(random_seed=42)

    features = {
        "transaction_count": 45.0,
        "incoming_count": 40.0,
        "outgoing_count": 5.0,
        "avg_amount_btc": 0.35,
        "amount_variance_btc": 1.25,
        "tx_frequency_per_day": 2.5,
        "tx_velocity_hourly": 0.45,
        "unique_counterparties": 35.0,
        "incoming_outgoing_ratio": 8.0,
        "activity_burst_count": 4.0,
        "connected_wallet_count": 35.0,
        "peel_chain_indicator": 0.40
    }

    raw_a, norm_a, class_a, is_anom_a = service_a.score_features(features)
    raw_b, norm_b, class_b, is_anom_b = service_b.score_features(features)

    assert raw_a == raw_b
    assert norm_a == norm_b
    assert class_a == class_b
    assert is_anom_a == is_anom_b

# 5. Model Info Endpoint Test (No Fake Accuracy)
def test_ml_model_info():
    response = client.get("/api/v1/ml/model-info")
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "IsolationForest"
    assert data["algorithm_type"] == "Unsupervised Ensemble Anomaly Detection"
    assert data["n_estimators"] == 100
    assert data["contamination"] == 0.10
    assert data["random_state"] == 42
    # Verify no false claim of classification accuracy
    assert "accuracy" not in data or data.get("accuracy") is None
    assert "Does not report synthetic accuracy" in data["evaluation_methodology"]

# 6. API Analyze & History Persistence Test
def test_ml_analyze_api_endpoint():
    test_addr = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"

    mock_tx = TransactionResponse(
        txid="00000000000000000000000000000000000000000000000000000000000000aa",
        block_height=100000,
        block_time=1600000000,
        block_time_iso="2020-09-13 12:26:40 UTC",
        confirmed=True,
        fee_sats=10000,
        fee_btc=0.0001,
        net_value_sats=50000000,
        net_value_btc=0.5,
        flow_direction="INCOMING",
        inputs=[TxIO(address="1Miner00000000000000000000000000001", value_sats=50010000, value_btc=0.5001)],
        outputs=[TxIO(address=test_addr, value_sats=50000000, value_btc=0.5)],
        data_source="Mock"
    )

    with patch("backend.app.services.blockchain_service.blockchain_service.get_wallet_transactions", new_callable=AsyncMock) as mock_get_txs:
        mock_get_txs.return_value = [mock_tx]

        # Analyze POST
        response = client.post(f"/api/v1/ml/analyze/{test_addr}")
        assert response.status_code == 201
        data = response.json()
        assert data["wallet_address"] == test_addr
        assert data["classification"] in ("NORMAL", "LOW ANOMALY", "MEDIUM ANOMALY", "HIGH ANOMALY")
        assert 0.0 <= data["normalized_score"] <= 100.0
        assert "investigative indicator and does not establish criminal activity" in data["explanation"]
        assert "INVESTIGATIVE FORENSIC DISCLAIMER" in data["disclaimer"]

        # History GET
        hist_response = client.get(f"/api/v1/ml/history/{test_addr}")
        assert hist_response.status_code == 200
        hist_data = hist_response.json()
        assert len(hist_data) >= 1
        assert hist_data[0]["wallet_address"] == test_addr

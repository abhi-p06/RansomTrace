import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.analytics_service import analytics_service
from backend.app.schemas.wallet import TransactionResponse, TxIO

client = TestClient(app)

def test_analytics_zero_transactions():
    """Verify zero division safeguards on empty transaction list."""
    res = analytics_service.calculate_wallet_analytics(
        address="1EmptyWalletAddress111111111111111",
        address_type="Legacy (P2PKH)",
        txs=[]
    )
    assert res.total_tx_count == 0
    assert res.incoming_tx_count == 0
    assert res.outgoing_tx_count == 0
    assert res.incoming_outgoing_ratio == 0.0
    assert res.avg_tx_amount_btc == 0.0
    assert res.median_tx_amount_btc == 0.0
    assert res.tx_amount_std_dev_btc == 0.0
    assert res.burst_count == 0
    assert res.unique_counterparties_count == 0
    assert len(res.amount_distribution) == 5

def test_analytics_single_transaction():
    """Verify single transaction statistics without std dev errors."""
    single_tx = TransactionResponse(
        txid="0000000000000000000000000000000000000000000000000000000000000001",
        block_height=100000,
        block_time=1600000000,
        block_time_iso="2020-09-13 12:26:40 UTC",
        confirmed=True,
        fee_sats=10000,
        fee_btc=0.0001,
        net_value_sats=50000000,  # 0.5 BTC
        net_value_btc=0.5,
        flow_direction="INCOMING",
        inputs=[TxIO(address="1SenderAddressAlpha00000000000001", value_sats=50010000, value_btc=0.5001)],
        outputs=[TxIO(address="1TargetWalletAddress0000000000001", value_sats=50000000, value_btc=0.5)],
        data_source="Test"
    )

    res = analytics_service.calculate_wallet_analytics(
        address="1TargetWalletAddress0000000000001",
        address_type="Legacy (P2PKH)",
        txs=[single_tx]
    )
    assert res.total_tx_count == 1
    assert res.incoming_tx_count == 1
    assert res.outgoing_tx_count == 0
    assert res.incoming_outgoing_ratio == 1.0
    assert res.avg_tx_amount_btc == 0.5
    assert res.median_tx_amount_btc == 0.5
    assert res.min_amount_btc == 0.5
    assert res.max_amount_btc == 0.5
    assert res.tx_amount_std_dev_btc == 0.0
    assert res.unique_counterparties_count == 1
    assert res.top_counterparties[0].address == "1SenderAddressAlpha00000000000001"

def test_analytics_manually_verified_calculations():
    """Verify exact mathematical formulas on controlled multi-tx dataset."""
    # 3 incoming txs (1.0, 2.0, 3.0 BTC) + 1 outgoing tx (4.0 BTC)
    # Total received: 6.0 BTC, Total sent: 4.0 BTC, Balance: 2.0 BTC
    # Amounts: [1.0, 2.0, 3.0, 4.0] BTC
    # Mean: 2.5 BTC, Median: 3.0 (or 2.5), Min: 1.0, Max: 4.0
    # Times: 1600000000, 1600000600 (10 min later), 1600001200 (10 min later) -> Cluster of 3 within 20m -> 1 burst!
    base_time = 1600000000
    tx1 = TransactionResponse(
        txid="tx1" + "0" * 61,
        block_time=base_time,
        confirmed=True,
        fee_sats=5000,
        fee_btc=0.00005,
        net_value_sats=100000000,  # 1.0 BTC
        net_value_btc=1.0,
        flow_direction="INCOMING",
        inputs=[TxIO(address="1SenderA000000000000000000000001", value_sats=100000000, value_btc=1.0)],
        outputs=[TxIO(address="1Target0000000000000000000000001", value_sats=100000000, value_btc=1.0)],
        data_source="Test"
    )
    tx2 = TransactionResponse(
        txid="tx2" + "0" * 61,
        block_time=base_time + 600,
        confirmed=True,
        fee_sats=5000,
        fee_btc=0.00005,
        net_value_sats=200000000,  # 2.0 BTC
        net_value_btc=2.0,
        flow_direction="INCOMING",
        inputs=[TxIO(address="1SenderB000000000000000000000001", value_sats=200000000, value_btc=2.0)],
        outputs=[TxIO(address="1Target0000000000000000000000001", value_sats=200000000, value_btc=2.0)],
        data_source="Test"
    )
    tx3 = TransactionResponse(
        txid="tx3" + "0" * 61,
        block_time=base_time + 1200,
        confirmed=True,
        fee_sats=5000,
        fee_btc=0.00005,
        net_value_sats=300000000,  # 3.0 BTC
        net_value_btc=3.0,
        flow_direction="INCOMING",
        inputs=[TxIO(address="1SenderC000000000000000000000001", value_sats=300000000, value_btc=3.0)],
        outputs=[TxIO(address="1Target0000000000000000000000001", value_sats=300000000, value_btc=3.0)],
        data_source="Test"
    )
    tx4 = TransactionResponse(
        txid="tx4" + "0" * 61,
        block_time=base_time + 86400,  # next day
        confirmed=True,
        fee_sats=5000,
        fee_btc=0.00005,
        net_value_sats=-400000000,  # 4.0 BTC out
        net_value_btc=-4.0,
        flow_direction="OUTGOING",
        inputs=[TxIO(address="1Target0000000000000000000000001", value_sats=400000000, value_btc=4.0)],
        outputs=[TxIO(address="1ReceiverX000000000000000000001", value_sats=400000000, value_btc=4.0)],
        data_source="Test"
    )

    res = analytics_service.calculate_wallet_analytics(
        address="1Target0000000000000000000000001",
        address_type="Legacy (P2PKH)",
        txs=[tx1, tx2, tx3, tx4]
    )
    assert res.total_tx_count == 4
    assert res.incoming_tx_count == 3
    assert res.outgoing_tx_count == 1
    assert res.incoming_outgoing_ratio == 3.0
    assert res.total_received_btc == 6.0
    assert res.total_sent_btc == 4.0
    assert res.current_balance_btc == 2.0
    assert res.avg_tx_amount_btc == 2.5
    assert res.min_amount_btc == 1.0
    assert res.max_amount_btc == 4.0
    assert res.burst_count == 1
    assert res.unique_counterparties_count == 4

def test_analytics_api_endpoint_live():
    res = client.get("/api/v1/wallets/13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94/analytics")
    assert res.status_code == 200
    data = res.json()
    assert data["address"] == "13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94"
    assert data["total_tx_count"] > 0
    assert len(data["amount_distribution"]) == 5
    assert len(data["volume_over_time"]) > 0
    assert "data_source" in data

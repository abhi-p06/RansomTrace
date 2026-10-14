import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.mempool_client import validate_bitcoin_address

client = TestClient(app)

def test_validate_bitcoin_address_formats():
    # Valid P2PKH (WannaCry)
    res_p2pkh = validate_bitcoin_address("13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94")
    assert res_p2pkh["valid"] is True
    assert res_p2pkh["type"] == "Legacy (P2PKH)"

    # Valid Bech32 (SegWit)
    res_bech32 = validate_bitcoin_address("bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq")
    assert res_bech32["valid"] is True
    assert "SegWit" in res_bech32["type"]

    # Invalid empty
    res_empty = validate_bitcoin_address("")
    assert res_empty["valid"] is False

    # Invalid prefix
    res_invalid_prefix = validate_bitcoin_address("9abcdef1234567890")
    assert res_invalid_prefix["valid"] is False

    # Invalid checksum
    res_invalid_checksum = validate_bitcoin_address("13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb99")
    assert res_invalid_checksum["valid"] is False
    assert "checksum" in res_invalid_checksum["reason"].lower()

def test_wallet_endpoint_invalid_address():
    res = client.get("/api/v1/wallets/not_a_bitcoin_address_xyz")
    assert res.status_code == 400
    assert "Invalid Bitcoin address" in res.json()["detail"]

def test_wallet_transactions_invalid_address():
    res = client.get("/api/v1/wallets/bad_addr/transactions")
    assert res.status_code == 400

def test_transaction_invalid_txid():
    res = client.get("/api/v1/transactions/not-a-valid-hex-txid")
    assert res.status_code == 400
    assert "64-character hexadecimal" in res.json()["detail"]

def test_wallet_endpoint_valid_public_data():
    # Query known public address
    res = client.get("/api/v1/wallets/13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94")
    assert res.status_code == 200
    data = res.json()
    assert data["address"] == "13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94"
    assert data["address_type"] == "Legacy (P2PKH)"
    assert data["total_received_sats"] > 0
    assert data["tx_count"] > 0
    assert "Public Bitcoin Blockchain" in data["data_source"]

def test_wallet_transactions_valid_public_data():
    res = client.get("/api/v1/wallets/13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94/transactions?limit=3")
    assert res.status_code == 200
    txs = res.json()
    assert len(txs) > 0
    tx = txs[0]
    assert "txid" in tx
    assert "confirmed" in tx
    assert "inputs" in tx
    assert "outputs" in tx
    assert tx["flow_direction"] in ("INCOMING", "OUTGOING", "INTERNAL", "TRANSIT")

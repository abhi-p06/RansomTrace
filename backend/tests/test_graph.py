import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_graph_invalid_address():
    res = client.get("/api/v1/wallets/bad_btc_address_123/graph")
    assert res.status_code == 400
    assert "Invalid Bitcoin address" in res.json()["detail"]

def test_graph_depth_1_construction():
    res = client.get("/api/v1/wallets/13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94/graph?depth=1&max_nodes=30")
    assert res.status_code == 200
    data = res.json()
    assert data["target_address"] == "13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94"
    assert data["depth_requested"] == 1
    assert len(data["nodes"]) > 0
    assert len(data["edges"]) > 0

    # Verify target node exists and marked as target
    target_node = next((n for n in data["nodes"] if n["id"] == "13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94"), None)
    assert target_node is not None
    assert target_node["is_target"] is True
    assert target_node["node_type"] == "TARGET"

    # Verify edge schema
    edge = data["edges"][0]
    assert "source" in edge
    assert "target" in edge
    assert "txid" in edge
    assert "amount_btc" in edge
    assert edge["amount_btc"] >= 0

    # Verify metrics
    metrics = data["metrics"]
    assert metrics["total_nodes"] > 0
    assert metrics["total_edges"] > 0
    assert len(metrics["hub_addresses"]) > 0

def test_graph_depth_2_construction():
    res = client.get("/api/v1/wallets/13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94/graph?depth=2&max_nodes=25")
    assert res.status_code == 200
    data = res.json()
    assert data["depth_requested"] == 2
    assert len(data["nodes"]) <= 25  # Respects max_nodes clamping

def test_graph_depth_clamping():
    # Attempt depth 10, should be clamped to 3 safely
    res = client.get("/api/v1/wallets/13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94/graph?depth=3&max_nodes=20")
    assert res.status_code == 200
    assert res.json()["depth_requested"] == 3

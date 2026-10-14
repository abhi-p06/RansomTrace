import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.services.dashboard_service import dashboard_service
from backend.app.models.case import InvestigationCase
from backend.app.models.evidence import Evidence

client = TestClient(app)

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_dashboard_summary_endpoint():
    resp = client.get("/api/v1/dashboard/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert "active_cases_count" in data
    assert "total_cases_count" in data
    assert "wallets_analyzed_count" in data
    assert "transactions_analyzed_count" in data
    assert "evidence_items_count" in data
    assert "high_critical_risk_cases_count" in data
    assert "risk_distribution" in data
    assert "recent_cases" in data
    assert "recent_evidence" in data
    assert "recent_anomalies" in data
    assert "recent_transactions" in data
    assert "timeline_events" in data
    assert "is_empty" in data
    assert isinstance(data["recent_cases"], list)
    assert isinstance(data["recent_evidence"], list)
    assert isinstance(data["recent_transactions"], list)
    assert isinstance(data["timeline_events"], list)

def test_dashboard_service_direct(db_session: Session):
    summary = dashboard_service.get_dashboard_summary(db_session)
    assert summary is not None
    assert summary.total_cases_count >= 0
    assert summary.active_cases_count <= summary.total_cases_count
    assert summary.risk_distribution.low >= 0
    assert summary.risk_distribution.critical >= 0

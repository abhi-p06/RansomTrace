import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.case import InvestigationCase, CaseStatus, CaseSeverity
from backend.app.models.custody import ChainOfCustodyEntry

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup():
    """Cleans up test cases created during tests."""
    yield
    db = SessionLocal()
    try:
        db.query(InvestigationCase).filter(
            InvestigationCase.case_id.like("TEST-%")
        ).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()

def test_create_case_success():
    payload = {
        "case_id": "TEST-2026-001",
        "title": "Operation BlackByte Extortion",
        "incident_type": "Ransomware Extortion",
        "description": "Analysis of multi-million dollar extortion demand.",
        "target_label": "Global Financial Services",
        "severity": "High",
        "status": "Investigating"
    }
    response = client.post("/api/v1/cases", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["case_id"] == "TEST-2026-001"
    assert data["title"] == "Operation BlackByte Extortion"
    assert data["severity"] == "High"
    assert data["status"] == "Investigating"
    assert "id" in data
    assert "created_at" in data

    # Verify Chain of Custody entry created in database
    db = SessionLocal()
    coc = db.query(ChainOfCustodyEntry).filter(
        ChainOfCustodyEntry.case_id == data["id"]
    ).first()
    assert coc is not None
    assert coc.action_performed == "CASE_INITIALIZED"
    db.close()

def test_create_case_duplicate_id_rejected():
    payload = {
        "case_id": "TEST-DUP-001",
        "title": "First Case",
        "incident_type": "Ransomware Extortion"
    }
    res1 = client.post("/api/v1/cases", json=payload)
    assert res1.status_code == 201

    # Attempt to create duplicate case_id
    res2 = client.post("/api/v1/cases", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"]

def test_create_case_validation_error():
    # Empty title
    payload = {
        "case_id": "TEST-ERR-001",
        "title": "   ",
        "incident_type": "Ransomware Extortion"
    }
    res = client.post("/api/v1/cases", json=payload)
    assert res.status_code == 422

def test_get_cases_list_and_filter():
    # Create two test cases
    client.post("/api/v1/cases", json={
        "case_id": "TEST-LIST-001",
        "title": "LockBit Attack Alpha",
        "incident_type": "Ransomware Extortion",
        "severity": "Critical",
        "status": "Open"
    })
    client.post("/api/v1/cases", json={
        "case_id": "TEST-LIST-002",
        "title": "Phishing Incident Beta",
        "incident_type": "Credential Phishing",
        "severity": "Low",
        "status": "Closed"
    })

    # List all
    res = client.get("/api/v1/cases")
    assert res.status_code == 200
    cases = res.json()
    assert len(cases) >= 2

    # Filter by status
    res_status = client.get("/api/v1/cases?status=Closed")
    assert res_status.status_code == 200
    for c in res_status.json():
        assert c["status"] == "Closed"

    # Filter by severity
    res_sev = client.get("/api/v1/cases?severity=Critical")
    assert res_sev.status_code == 200
    for c in res_sev.json():
        assert c["severity"] == "Critical"

    # Search keyword
    res_search = client.get("/api/v1/cases?search=LockBit")
    assert res_search.status_code == 200
    assert any("LockBit" in c["title"] for c in res_search.json())

def test_get_case_by_id_and_not_found():
    res = client.post("/api/v1/cases", json={
        "case_id": "TEST-GET-001",
        "title": "Target Investigation",
        "incident_type": "Ransomware Extortion"
    })
    case_data = res.json()

    # Query by formatted case_id
    res_by_num = client.get(f"/api/v1/cases/{case_data['case_id']}")
    assert res_by_num.status_code == 200
    assert res_by_num.json()["id"] == case_data["id"]

    # Query by UUID
    res_by_uuid = client.get(f"/api/v1/cases/{case_data['id']}")
    assert res_by_uuid.status_code == 200
    assert res_by_uuid.json()["case_id"] == "TEST-GET-001"

    # Query invalid
    res_404 = client.get("/api/v1/cases/NON-EXISTENT-CASE")
    assert res_404.status_code == 404

def test_update_case_status_and_severity():
    res = client.post("/api/v1/cases", json={
        "case_id": "TEST-UPD-001",
        "title": "Initial Title",
        "incident_type": "Ransomware Extortion",
        "severity": "Low",
        "status": "Open"
    })
    case_data = res.json()

    # Update to Contained and Critical
    update_res = client.put(f"/api/v1/cases/{case_data['case_id']}", json={
        "title": "Updated Escalated Incident",
        "severity": "Critical",
        "status": "Contained"
    })
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["title"] == "Updated Escalated Incident"
    assert updated["severity"] == "Critical"
    assert updated["status"] == "Contained"

    # Verify audit entry was appended to Chain of Custody
    db = SessionLocal()
    coc_entries = db.query(ChainOfCustodyEntry).filter(
        ChainOfCustodyEntry.case_id == case_data["id"]
    ).order_by(ChainOfCustodyEntry.timestamp.desc()).all()
    assert len(coc_entries) >= 2
    assert "CASE_DOSSIER_UPDATED" in [e.action_performed for e in coc_entries]
    db.close()

def test_delete_case_cascade():
    res = client.post("/api/v1/cases", json={
        "case_id": "TEST-DEL-001",
        "title": "Case to be Deleted",
        "incident_type": "Ransomware Extortion"
    })
    case_data = res.json()

    # Delete case
    del_res = client.delete(f"/api/v1/cases/{case_data['case_id']}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"

    # Verify no longer exists
    get_res = client.get(f"/api/v1/cases/{case_data['case_id']}")
    assert get_res.status_code == 404

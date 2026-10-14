import pytest
import io
import re
import base64
import zlib
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.case import InvestigationCase
from backend.app.models.evidence import Evidence
from backend.app.models.custody import ChainOfCustodyEntry
from backend.app.models.analysis import RiskAssessment, MLAnalysis
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
def test_case_with_artifacts(db_session: Session):
    case_uid = f"CASE-REPORT-TEST-{datetime.now().timestamp()}"
    case = InvestigationCase(
        case_id=case_uid,
        title="Automated PDF Report Verification Case",
        incident_type="Ransomware Payment Analysis",
        description="Comprehensive forensic dossier testing for Phase 9 implementation.",
        target_label="13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94",
        severity="Critical",
        status="Investigating"
    )
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    # Add evidence
    evidence = Evidence(
        case_id=case.id,
        artifact_type="TRANSACTION_SNAPSHOT",
        wallet_address="13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94",
        transaction_hash="4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b",
        amount_btc=0.5,
        source="Public Bitcoin Blockchain / Mempool API",
        description="Extortion ransom deposit from compromised enterprise node.",
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        captured_by="Lead Forensics Examiner Agent",
        raw_payload={"txid": "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b", "amount_sats": 50000000}
    )
    db_session.add(evidence)
    db_session.commit()
    db_session.refresh(evidence)

    # Add chain of custody
    custody = ChainOfCustodyEntry(
        case_id=case.id,
        evidence_id=evidence.id,
        action_performed="EVIDENCE_CAPTURED",
        actor_name="Agent Forensics",
        notes="Cryptographic SHA-256 seal established at capture time.",
        current_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )
    db_session.add(custody)

    # Add Risk Assessment
    risk = RiskAssessment(
        case_id=case.id,
        risk_score=85.5,
        risk_tier="Critical",
        heuristics_summary={
            "rule_score": 82.0,
            "ml_score": 89.0,
            "reasons": [
                "Extremely rapid outbound liquidation velocity (98.3% drained within 3 blocks)",
                "Peeling chain topology detected across 4 consolidation hops"
            ]
        },
        disclaimer="Investigative indicator based strictly on observable transaction behaviour."
    )
    db_session.add(risk)

    # Add ML Analysis
    ml = MLAnalysis(
        case_id=case.id,
        model_version="1.0.0-IsolationForest",
        raw_anomaly_score=-0.2850,
        normalized_score=91.2,
        classification="CRITICAL_ANOMALY",
        features_used={"velocity": 12.4, "burst": 4},
        explanation="High velocity dispersal topology matches ransomware extraction clusters."
    )
    db_session.add(ml)
    db_session.commit()

    return case

def test_report_preview_service(db_session: Session, test_case_with_artifacts):
    preview = forensic_report_service.get_report_preview_data(db_session, test_case_with_artifacts.id)
    assert preview.case_info.case_id == test_case_with_artifacts.case_id
    assert preview.case_info.severity == "Critical"
    assert preview.target_wallet == "13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94"
    assert preview.risk_summary is not None
    assert preview.risk_summary.final_score == 85.5
    assert preview.ml_classification == "CRITICAL_ANOMALY"
    assert len(preview.evidence_items) >= 1
    assert preview.chain_of_custody_count >= 1

def test_pdf_generation_bytes_and_structure(db_session: Session, test_case_with_artifacts):
    pdf_bytes = forensic_report_service.generate_pdf_report(db_session, test_case_with_artifacts.id)
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 5000
    assert pdf_bytes.startswith(b"%PDF-")

    # Decompress streams to verify all 17 sections and required forensic wording
    parts = re.findall(b"stream\n(.*?)(?:~>endstream|endstream)", pdf_bytes, re.DOTALL)
    full_text = ""
    for p in parts:
        p_clean = p.strip()
        if not p_clean.endswith(b"~>"):
            p_clean += b"~>"
        try:
            full_text += " " + zlib.decompress(base64.a85decode(p_clean, adobe=True)).decode("latin1", errors="ignore")
        except Exception:
            pass

    assert "RansomTrace" in full_text
    assert test_case_with_artifacts.case_id in full_text
    assert "OBSERVED FACTS" in full_text
    assert "ANALYTICAL INDICATORS" in full_text
    assert "INVESTIGATOR INTERPRETATION" in full_text
    assert "SHA-256" in full_text
    assert "Section 65B" in full_text
    assert "ISOLATION FOREST" in full_text
    assert "CHAIN OF CUSTODY" in full_text

def test_report_api_endpoints(test_case_with_artifacts):
    # Preview Endpoint
    resp_prev = client.get(f"/api/v1/cases/{test_case_with_artifacts.id}/report/preview")
    assert resp_prev.status_code == 200
    data = resp_prev.json()
    assert data["case_info"]["case_id"] == test_case_with_artifacts.case_id
    assert "disclaimer" in data

    # PDF Endpoint
    resp_pdf = client.get(f"/api/v1/cases/{test_case_with_artifacts.id}/report/pdf")
    assert resp_pdf.status_code == 200
    assert resp_pdf.headers["content-type"] == "application/pdf"
    assert f"filename=\"RansomTrace_Forensic_Report_{test_case_with_artifacts.id}.pdf\"" in resp_pdf.headers["content-disposition"]
    assert len(resp_pdf.content) > 5000
    assert resp_pdf.content.startswith(b"%PDF-")

def test_report_nonexistent_case():
    resp_prev = client.get("/api/v1/cases/NON_EXISTENT_CASE_ID/report/preview")
    assert resp_prev.status_code == 404

    resp_pdf = client.get("/api/v1/cases/NON_EXISTENT_CASE_ID/report/pdf")
    assert resp_pdf.status_code == 404


def test_report_generation_demo_data(db_session: Session):
    """
    Tests PDF generation on demonstration data ('CASE-DEMO-SYNTHETIC-001'),
    verifying all 13 required forensic sections, tripartite distinction,
    and academic non-attribution language.
    """
    import pypdf
    import io

    case_id = "CASE-DEMO-SYNTHETIC-001"

    # 1. Preview verification
    preview = forensic_report_service.get_report_preview_data(db_session, case_id)
    assert preview.case_info.case_id == case_id
    assert preview.target_wallet == "1DemoRansomCollectionWallet002"
    assert preview.analytics_summary is not None
    assert preview.analytics_summary.total_tx_count >= 1
    assert preview.risk_summary is not None
    assert len(preview.evidence_items) >= 1
    assert preview.chain_of_custody_count >= 1

    # 2. PDF compilation verification
    pdf_bytes = forensic_report_service.generate_pdf_report(db_session, case_id)
    assert pdf_bytes is not None
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 5000

    # 3. Extract and verify text content across all 13 sections
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    assert len(reader.pages) >= 2
    full_text = " ".join([p.extract_text() for p in reader.pages])

    required_sections = [
        "1. CASE INFORMATION [OBSERVED DATA]",
        "2. WALLET INFORMATION [OBSERVED DATA]",
        "3. TRANSACTION SUMMARY [OBSERVED DATA]",
        "4. TRANSACTION ANALYSIS (10 FORENSIC METRICS) [ANALYSIS]",
        "5. FUND-FLOW SUMMARY (DIRECT DEPTH-1) [ANALYSIS]",
        "6. AI ANOMALY DETECTION (ISOLATION FOREST) [ANALYSIS]",
        "7. INVESTIGATIVE RISK SCORE [INVESTIGATIVE INDICATORS]",
        "8. TRIGGERED RISK FACTORS [INVESTIGATIVE INDICATORS]",
        "9. DIGITAL EVIDENCE RECORDS [OBSERVED DATA]",
        "10. CRYPTOGRAPHIC SHA-256 INTEGRITY HASHES [OBSERVED DATA]",
        "11. APPEND-ONLY CHAIN OF CUSTODY HISTORY [OBSERVED DATA]",
        "12. FORENSIC & TECHNICAL LIMITATIONS [ANALYSIS]",
        "13. LEGAL & ETHICAL DISCLAIMER [STATUTORY NOTICE]",
    ]

    for section in required_sections:
        assert section.lower() in full_text.lower(), f"Missing section: {section}"

    # Verify Tripartite Distinction
    assert "observed data" in full_text.lower()
    assert "analysis" in full_text.lower()
    assert "investigative indicators" in full_text.lower()

    # Verify Non-Attribution / Academic Compliance
    assert "warrants further investigation" in full_text.lower()
    assert "does not make claims of criminal identity" in full_text.lower() or "not proof of ransomware activity" in full_text.lower()


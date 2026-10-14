import logging
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.services.report_service import forensic_report_service
from backend.app.schemas.report import ReportPreviewResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Forensic Investigation Reports"])


@router.get(
    "/cases/{case_id}/report/preview",
    response_model=ReportPreviewResponse,
    summary="Get Case Forensic Report Preview Metadata"
)
def get_case_report_preview(
    case_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns structured preview metadata for the forensic report, allowing investigators
    to review case status, target wallet findings, and evidence count prior to PDF generation.
    """
    try:
        preview = forensic_report_service.get_report_preview_data(db=db, case_id=case_id)
        return preview
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Error preparing report preview for case {case_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Report preview generation encountered an internal error."
        )


@router.get(
    "/cases/{case_id}/report/pdf",
    summary="Generate & Download Case Forensic Investigation PDF Report"
)
@router.get(
    "/reports/{case_id}/pdf",
    summary="Generate & Download Case Forensic Investigation PDF Report (Alias)"
)
def download_case_pdf_report(
    case_id: str,
    db: Session = Depends(get_db)
):
    """
    GENERATE FORENSIC REPORT (PDF):
    Compiles an academic and judicial-grade PDF forensic investigation report containing:
    1. RansomTrace Title & Case Dossier Metadata
    2. Explicit Tripartite Evidentiary Distinction (Observed Facts vs Indicators vs Interpretation)
    3. Incident Background & Target Wallet Statistics
    4. Hybrid Risk Scoring & Behavioral Rules Matrix
    5. Isolation Forest Unsupervised Anomaly Detection Analysis
    6. Digital Evidence Inventory with 64-char Canonical SHA-256 Hashes
    7. Append-Only Chain of Custody Provenance Log
    8. Technical Boundaries & Section 65B Legal Disclaimer
    """
    try:
        import re
        clean_id = re.sub(r"[^A-Za-z0-9_-]", "_", case_id)[:64]
        pdf_bytes = forensic_report_service.generate_pdf_report(db=db, case_id=case_id)
        safe_filename = f"RansomTrace_Forensic_Report_{clean_id}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{safe_filename}"',
                "Content-Type": "application/pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Error compiling forensic PDF report for case {case_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate forensic PDF report due to an internal error."
        )

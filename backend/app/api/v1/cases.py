import hashlib
import random
import string
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.core.database import get_db
from backend.app.models.case import InvestigationCase, CaseStatus, CaseSeverity
from backend.app.models.custody import ChainOfCustodyEntry
from backend.app.schemas.case import CaseCreate, CaseUpdate, CaseResponse

router = APIRouter(prefix="/cases", tags=["Investigation Cases"])

def generate_case_id() -> str:
    """Generates an academic forensic case number if not supplied."""
    suffix = "".join(random.choices(string.digits, k=4))
    return f"RT-2026-{suffix}"

def find_case_by_identifier(db: Session, identifier: str) -> Optional[InvestigationCase]:
    """Finds case by internal UUID or formatted case_id with safe length limits."""
    clean_id = identifier.strip()[:64]
    return db.query(InvestigationCase).filter(
        or_(InvestigationCase.id == clean_id, InvestigationCase.case_id == clean_id)
    ).first()

def to_case_response(case: InvestigationCase) -> CaseResponse:
    """Helper to convert model to response schema with counts."""
    return CaseResponse(
        id=case.id,
        case_id=case.case_id,
        title=case.title,
        incident_type=case.incident_type,
        description=case.description,
        target_label=case.target_label,
        severity=case.severity,
        status=case.status,
        created_at=case.created_at,
        updated_at=case.updated_at,
        wallet_count=len(case.wallets) if case.wallets else 0,
        evidence_count=len(case.evidences) if case.evidences else 0
    )

@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED, summary="Create Investigation Case")
def create_case(case_in: CaseCreate, db: Session = Depends(get_db)):
    """
    Creates a new cybercrime investigation case dossier with real relational database persistence.
    Also initializes an initial Chain-of-Custody record for forensic traceability.
    """
    case_id = case_in.case_id.strip() if case_in.case_id else generate_case_id()

    # Check case_id uniqueness
    existing = db.query(InvestigationCase).filter(InvestigationCase.case_id == case_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Investigation case with ID '{case_id}' already exists."
        )

    new_case = InvestigationCase(
        case_id=case_id,
        title=case_in.title.strip(),
        incident_type=case_in.incident_type.strip(),
        description=case_in.description.strip() if case_in.description else None,
        target_label=case_in.target_label.strip() if case_in.target_label else None,
        severity=case_in.severity.value,
        status=case_in.status.value
    )

    db.add(new_case)
    db.flush()

    # Create initial Chain of Custody entry
    initial_hash = hashlib.sha256(f"INIT:{new_case.id}:{new_case.case_id}:{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()
    coc_entry = ChainOfCustodyEntry(
        case_id=new_case.id,
        action_performed="CASE_INITIALIZED",
        actor_name="Lead Cyber Investigator",
        notes=f"Investigation dossier opened for incident: {new_case.title}",
        previous_hash="GENESIS_BLOCK",
        current_hash=initial_hash
    )
    db.add(coc_entry)
    db.commit()
    db.refresh(new_case)

    return to_case_response(new_case)

@router.get("", response_model=List[CaseResponse], summary="List Investigation Cases")
def list_cases(
    status_filter: Optional[CaseStatus] = Query(None, alias="status"),
    severity_filter: Optional[CaseSeverity] = Query(None, alias="severity"),
    search: Optional[str] = Query(None, description="Search by title, case_id, or target_label"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Retrieves all investigation cases with optional filtering, search, and pagination.
    """
    query = db.query(InvestigationCase)

    if status_filter:
        query = query.filter(InvestigationCase.status == status_filter.value)
    if severity_filter:
        query = query.filter(InvestigationCase.severity == severity_filter.value)
    if search:
        clean_search = search.strip()[:100]
        search_pattern = f"%{clean_search}%"
        query = query.filter(
            or_(
                InvestigationCase.title.ilike(search_pattern),
                InvestigationCase.case_id.ilike(search_pattern),
                InvestigationCase.target_label.ilike(search_pattern)
            )
        )

    cases = query.order_by(InvestigationCase.created_at.desc()).offset(skip).limit(limit).all()
    return [to_case_response(c) for c in cases]

@router.get("/{case_id}", response_model=CaseResponse, summary="Get Case Details")
def get_case(case_id: str, db: Session = Depends(get_db)):
    """
    Retrieves single case dossier by internal UUID or formatted case_id.
    """
    case = find_case_by_identifier(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation case '{case_id}' was not found in the forensic registry."
        )
    return to_case_response(case)

@router.put("/{case_id}", response_model=CaseResponse, summary="Update Case Dossier")
def update_case(case_id: str, case_update: CaseUpdate, db: Session = Depends(get_db)):
    """
    Updates an investigation case, including changing status or severity.
    Logs updates to the Chain of Custody ledger for forensic audit integrity.
    """
    case = find_case_by_identifier(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation case '{case_id}' was not found."
        )

    changes = []
    if case_update.title is not None and case_update.title.strip() != case.title:
        changes.append(f"Title changed to '{case_update.title.strip()}'")
        case.title = case_update.title.strip()

    if case_update.incident_type is not None and case_update.incident_type.strip() != case.incident_type:
        changes.append(f"Incident type changed to '{case_update.incident_type.strip()}'")
        case.incident_type = case_update.incident_type.strip()

    if case_update.description is not None:
        case.description = case_update.description.strip() or None

    if case_update.target_label is not None:
        case.target_label = case_update.target_label.strip() or None

    if case_update.severity is not None and case_update.severity.value != case.severity:
        changes.append(f"Severity modified: {case.severity} -> {case_update.severity.value}")
        case.severity = case_update.severity.value

    if case_update.status is not None and case_update.status.value != case.status:
        changes.append(f"Status transition: {case.status} -> {case_update.status.value}")
        case.status = case_update.status.value

    if changes:
        case.updated_at = datetime.now(timezone.utc)
        # Log to Chain of Custody
        prev_entry = db.query(ChainOfCustodyEntry).filter(
            ChainOfCustodyEntry.case_id == case.id
        ).order_by(ChainOfCustodyEntry.timestamp.desc()).first()
        prev_hash = prev_entry.current_hash if prev_entry else "GENESIS_BLOCK"

        update_hash = hashlib.sha256(f"UPDATE:{case.id}:{'; '.join(changes)}:{case.updated_at.isoformat()}".encode()).hexdigest()
        coc_entry = ChainOfCustodyEntry(
            case_id=case.id,
            action_performed="CASE_DOSSIER_UPDATED",
            actor_name="Lead Cyber Investigator",
            notes="; ".join(changes),
            previous_hash=prev_hash,
            current_hash=update_hash
        )
        db.add(coc_entry)

    db.commit()
    db.refresh(case)
    return to_case_response(case)

@router.delete("/{case_id}", status_code=status.HTTP_200_OK, summary="Delete Investigation Case")
def delete_case(case_id: str, db: Session = Depends(get_db)):
    """
    Deletes an investigation case and cascades to associated forensic artifacts.
    """
    case = find_case_by_identifier(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation case '{case_id}' was not found."
        )

    deleted_case_id = case.case_id
    db.delete(case)
    db.commit()

    return {
        "status": "success",
        "detail": f"Investigation case '{deleted_case_id}' and all associated records have been purged.",
        "case_id": deleted_case_id
    }

@router.post("/demo/load", summary="Load Synthetic Demonstration Dataset")
def load_synthetic_demo_data(force: bool = False, db: Session = Depends(get_db)):
    """
    Initializes or reloads the benchmark synthetic demonstration dataset.
    Clearly marked as 'DEMONSTRATION DATA — SYNTHETIC'.
    Does not claim to represent any real ransomware incident.
    """
    from backend.app.services.data_layer import load_demo_data
    return load_demo_data(db, force_reload=force)


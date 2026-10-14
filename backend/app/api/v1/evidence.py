import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.services.evidence_service import evidence_service
from backend.app.schemas.evidence import (
    EvidenceCreate,
    EvidenceResponse,
    EvidenceDetailResponse,
    ChainOfCustodyCreate,
    ChainOfCustodyResponse,
    IntegrityVerificationResponse,
    SimpleEvidenceRecord,
    PreserveTransactionRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Digital Forensics & Evidence Management"])


@router.post(
    "/evidence/preserve-transaction",
    response_model=SimpleEvidenceRecord,
    status_code=status.HTTP_201_CREATED,
    summary="PRESERVE AS EVIDENCE: Preserve Transaction Finding"
)
def preserve_transaction_evidence(
    payload: PreserveTransactionRequest,
    db: Session = Depends(get_db)
):
    """
    PRESERVE AS EVIDENCE:
    Creates a simple, immutable digital evidence record from a Bitcoin transaction.
    Generates a deterministic canonical representation and computes a cryptographic SHA-256 fingerprint.
    """
    try:
        return evidence_service.preserve_transaction(db=db, req=payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Error preserving transaction evidence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to preserve transaction evidence."
        )


@router.post(
    "/evidence",
    response_model=EvidenceDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Preserve Blockchain Finding as Digital Evidence"
)
def create_evidence_record(
    payload: EvidenceCreate,
    db: Session = Depends(get_db)
):
    """
    PRESERVE AS EVIDENCE:
    Preserves a blockchain transaction, wallet finding, or graph cluster into the immutable evidence locker.
    1. Validates associated case
    2. Serializes data into a canonical byte representation
    3. Generates cryptographic SHA-256 fingerprint
    4. Automatically records initial Chain of Custody entries (COLLECTED, HASHED, STORED)
    """
    try:
        evidence = evidence_service.create_evidence(db=db, payload=payload)
        return evidence
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Error preserving digital evidence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to preserve evidence due to an internal processing error."
        )


@router.get(
    "/evidence",
    response_model=List[EvidenceResponse],
    summary="List Preserved Digital Evidence Items"
)
def list_evidence_records(
    case_id: Optional[str] = Query(None, description="Filter by Investigation Case ID"),
    artifact_type: Optional[str] = Query(None, description="Filter by artifact type"),
    wallet_address: Optional[str] = Query(None, description="Filter by wallet address"),
    db: Session = Depends(get_db)
):
    """Retrieves list of preserved digital evidence artifacts matching filter criteria."""
    return evidence_service.list_evidence(
        db=db,
        case_id=case_id,
        artifact_type=artifact_type,
        wallet_address=wallet_address
    )


@router.get(
    "/evidence/{evidence_id}",
    response_model=EvidenceDetailResponse,
    summary="Get Evidence Record with Full Chain of Custody"
)
def get_evidence_detail(
    evidence_id: str,
    db: Session = Depends(get_db)
):
    """Retrieves complete forensic dossier for an evidence artifact, including its chronological Chain of Custody."""
    evidence = evidence_service.get_evidence_detail(db=db, evidence_id=evidence_id)
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidence with ID '{evidence_id}' was not found in the evidence locker."
        )
    return evidence


@router.post(
    "/evidence/{evidence_id}/verify",
    response_model=IntegrityVerificationResponse,
    summary="Cryptographically Verify Evidence SHA-256 Integrity"
)
def verify_evidence_integrity(
    evidence_id: str,
    verifier_name: str = Query("Lead Forensic Examiner", description="Name of investigator conducting verification"),
    db: Session = Depends(get_db)
):
    """
    EVIDENCE INTEGRITY VERIFICATION:
    Recalculates the canonical SHA-256 hash of the stored data payload and compares it against
    the immutable stored fingerprint. Appends a new VERIFIED entry to the Chain of Custody.
    """
    try:
        result = evidence_service.verify_evidence_integrity(
            db=db,
            evidence_id=evidence_id,
            actor_name=verifier_name
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Error verifying integrity for evidence {evidence_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Integrity verification failed due to an internal processing error."
        )


@router.post(
    "/evidence/{evidence_id}/custody",
    response_model=ChainOfCustodyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Append Custodial Action to Chain of Custody"
)
def append_custody_action(
    evidence_id: str,
    payload: ChainOfCustodyCreate,
    db: Session = Depends(get_db)
):
    """
    APPEND-ONLY CHAIN OF CUSTODY:
    Appends a verifiable custodial event (e.g. REVIEWED, EXPORTED, EXAMINED) to the tamper-evident provenance log.
    """
    effective_action = payload.action or payload.action_performed or ""
    effective_actor = payload.actor or payload.actor_name or ""
    if not effective_action:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Custody action must be specified.")
    if not effective_actor:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Actor name must be specified.")

    try:
        entry = evidence_service.append_custody_action(
            db=db,
            evidence_id=evidence_id,
            action=effective_action,
            actor=effective_actor,
            notes=payload.notes
        )
        return entry
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Error appending custody action: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record custody action due to an internal processing error."
        )


@router.get(
    "/evidence/{evidence_id}/custody",
    response_model=List[ChainOfCustodyResponse],
    summary="Get Chronological Chain of Custody Timeline for Evidence"
)
def get_evidence_custody_timeline(
    evidence_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns the complete chronological Chain of Custody record for an evidence item.
    """
    evidence = evidence_service.get_evidence_detail(db=db, evidence_id=evidence_id)
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidence with ID '{evidence_id}' was not found."
        )
    return evidence_service.get_custody_timeline(db=db, evidence_id=evidence_id)


@router.put(
    "/evidence/{evidence_id}/custody/{entry_id}",
    summary="IMMUTABILITY ENFORCEMENT: Disallow Editing Custody Entries"
)
@router.patch(
    "/evidence/{evidence_id}/custody/{entry_id}",
    summary="IMMUTABILITY ENFORCEMENT: Disallow Editing Custody Entries"
)
def disallow_editing_custody_entry(evidence_id: str, entry_id: str):
    """
    IMMUTABILITY ENFORCEMENT:
    Prevents modifying previously recorded Chain of Custody entries.
    Forensic audit entries are append-only.
    """
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Chain of custody entries are strictly immutable and cannot be edited. New actions must be appended."
    )


@router.get(
    "/cases/{case_id}/evidence",
    response_model=List[EvidenceResponse],
    summary="Get All Evidence Preserved for a Specific Case"
)
def get_case_evidence(
    case_id: str,
    db: Session = Depends(get_db)
):
    """Convenience endpoint listing all evidence items associated with an Investigation Case."""
    return evidence_service.list_evidence(db=db, case_id=case_id)

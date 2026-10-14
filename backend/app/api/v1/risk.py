import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.services.blockchain_service import blockchain_service
from backend.app.services.mempool_client import validate_bitcoin_address
from backend.app.services.risk_service import RiskScoringService, DISCLAIMER_TEXT
from backend.app.schemas.risk import (
    RiskAssessmentResponse,
    RiskAssessmentHistoryItem,
    RiskAssessmentRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Investigative Risk Scoring"])

risk_service = RiskScoringService()


@router.post(
    "/risk/assess",
    response_model=RiskAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Calculate Hybrid Investigative Risk Score from Request Body"
)
async def assess_wallet_risk_body(
    request_body: RiskAssessmentRequest,
    db: Session = Depends(get_db)
):
    if not request_body or not request_body.wallet_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet address is required in request body."
        )
    return await assess_wallet_risk(
        wallet_address=request_body.wallet_address,
        case_id=request_body.case_id,
        include_ml=request_body.include_ml,
        request_body=request_body,
        db=db
    )


@router.post(
    "/risk/assess/{wallet_address}",
    response_model=RiskAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Calculate Hybrid Investigative Risk Score for Wallet Address"
)
async def assess_wallet_risk(
    wallet_address: str,
    case_id: Optional[str] = Query(None, description="Optional Investigation Case ID"),
    include_ml: bool = Query(True, description="Whether to include ML Isolation Forest anomaly score"),
    request_body: Optional[RiskAssessmentRequest] = Body(None),
    db: Session = Depends(get_db)
):
    """
    Executes the hybrid forensic risk-scoring pipeline:
    1. Evaluates 7 transparent, observable behavioral rules (0-100 pts)
    2. Runs scikit-learn Isolation Forest Anomaly Detection (0-100 pts)
    3. Calculates calibrated weighted final score (0-100 pts)
    4. Categorizes into operational tiers: LOW (0-29), MEDIUM (30-59), HIGH (60-79), CRITICAL (80-100)
    5. Preserves full audit record in PostgreSQL / SQLite

    CRITICAL NOTICE: The risk score is an investigative prioritization indicator based strictly on
    observable transaction behaviour. It does NOT establish criminal liability or identify a person.
    """
    clean_addr = wallet_address.strip()
    val = validate_bitcoin_address(clean_addr)
    if not val["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Bitcoin address: {val['reason']}"
        )

    effective_case_id = case_id
    effective_include_ml = include_ml
    if request_body:
        if request_body.case_id:
            effective_case_id = request_body.case_id
        if request_body.include_ml is not None:
            effective_include_ml = request_body.include_ml

    try:
        # Retrieve recent transaction history
        txs = await blockchain_service.get_wallet_transactions(clean_addr, db, limit=100)

        # Run hybrid scoring engine
        assessment = risk_service.assess_wallet(
            db=db,
            wallet_address=clean_addr,
            txs=txs,
            case_id=effective_case_id,
            include_ml=effective_include_ml
        )
        return assessment

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        logger.error(f"Blockchain service error during risk assessment for {clean_addr}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Public blockchain data service is currently unavailable for risk assessment."
        )
    except Exception as e:
        logger.exception(f"Unexpected error running risk assessment on {clean_addr}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Forensic risk assessment failed due to an internal processing error."
        )


@router.get(
    "/risk/history/{wallet_address}",
    response_model=List[RiskAssessmentHistoryItem],
    summary="Get Past Risk Assessments for a Wallet"
)
def get_risk_history(
    wallet_address: str,
    limit: int = Query(10, ge=1, le=50, description="Max history records to return"),
    db: Session = Depends(get_db)
):
    """
    Returns audit history of prior risk assessments for the specified wallet.
    """
    clean_addr = wallet_address.strip()
    val = validate_bitcoin_address(clean_addr)
    if not val["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Bitcoin address: {val['reason']}"
        )

    return risk_service.get_history(db=db, wallet_address=clean_addr, limit=limit)


@router.get(
    "/risk/rules",
    summary="Get All Behavioral Rules, Weights and Tiers"
)
def get_risk_rules():
    """
    Returns transparency specifications for the 5 observable indicators, weighting formulas, and risk tiers.
    """
    return {
        "disclaimer": DISCLAIMER_TEXT,
        "weighting": {
            "total_max_score": 100.0,
            "weights": {
                "high_tx_frequency": 20.0,
                "high_amount_variation": 15.0,
                "large_counterparties": 20.0,
                "rapid_movement": 20.0,
                "ml_anomaly_result": 25.0,
            },
        },
        "tiers": [
            {"range": "0 - 29", "tier": "LOW", "description": "Standard personal or dormant wallet behavior"},
            {"range": "30 - 59", "tier": "MEDIUM", "description": "Moderate behavioral deviations or counterparty activity"},
            {"range": "60 - 79", "tier": "HIGH", "description": "Significant risk indicators, rapid velocity, and broad counterparty churn"},
            {"range": "80 - 100", "tier": "CRITICAL", "description": "Severe transaction frequency, rapid movement, high variation, and strong ML anomaly"}
        ],
        "indicators": [
            {"id": "RULE_TX_FREQUENCY", "name": "High transaction frequency", "max_score": 20.0, "category": "Frequency"},
            {"id": "RULE_AMOUNT_VARIATION", "name": "High transaction amount variation", "max_score": 15.0, "category": "Variance"},
            {"id": "RULE_COUNTERPARTIES", "name": "Large number of counterparties", "max_score": 20.0, "category": "Network"},
            {"id": "RULE_RAPID_MOVEMENT", "name": "Rapid movement of funds", "max_score": 20.0, "category": "Velocity"},
            {"id": "RULE_ML_ANOMALY", "name": "ML anomaly result", "max_score": 25.0, "category": "Machine Learning"}
        ]
    }

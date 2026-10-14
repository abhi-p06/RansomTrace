import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.services.blockchain_service import blockchain_service
from backend.app.services.mempool_client import validate_bitcoin_address
from backend.app.services.ml_service import MLAnomalyService
from backend.app.schemas.ml import (
    MLAnalysisResponse,
    MLAnalysisHistoryItem,
    ModelInfo,
    MLAnalysisRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Forensic Machine Learning"])

# Singleton ML Anomaly Service instance (seeded with random_seed=42 for reproducibility)
ml_anomaly_service = MLAnomalyService(random_seed=42)


@router.post(
    "/ml/analyze",
    response_model=MLAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Run Isolation Forest Anomaly Detection from Request Body"
)
async def analyze_wallet_body(
    request_body: MLAnalysisRequest,
    db: Session = Depends(get_db)
):
    if not request_body or not request_body.wallet_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet address is required in request body."
        )
    return await analyze_wallet(
        wallet_address=request_body.wallet_address,
        case_id=request_body.case_id,
        request_body=request_body,
        db=db
    )


@router.post(
    "/ml/analyze/{wallet_address}",
    response_model=MLAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Run Isolation Forest Anomaly Detection on Wallet Address"
)
async def analyze_wallet(
    wallet_address: str,
    case_id: Optional[str] = Query(None, description="Optional Investigation Case ID to associate with this scan"),
    request_body: Optional[MLAnalysisRequest] = Body(None),
    db: Session = Depends(get_db)
):
    """
    Executes the forensic machine-learning anomaly detection pipeline for a Bitcoin address:
    1. Blockchain Transaction Retrieval & Cleaning
    2. 12-Feature Behavioral Extraction (Frequency, Velocity, Peel Ratio, Variance, Bursts)
    3. Scikit-learn Isolation Forest Tree Isolation Path Scoring
    4. Calibrated Normalization to 0-100 Risk Indicator
    5. Explainable AI Factor Attribution
    6. Persistence to PostgreSQL / SQLite database

    NOTE: This is an investigative anomaly-detection system. Statistical anomaly does NOT
    establish criminal liability or prove ransomware association.
    """
    clean_addr = wallet_address.strip()
    val = validate_bitcoin_address(clean_addr)
    if not val["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Bitcoin address: {val['reason']}"
        )

    # Use case_id from query param or request body
    effective_case_id = case_id
    if not effective_case_id and request_body and request_body.case_id:
        effective_case_id = request_body.case_id

    try:
        # Retrieve recent transaction history (up to 100 txs) from public blockchain layer
        txs = await blockchain_service.get_wallet_transactions(clean_addr, db, limit=100)

        # Run ML Pipeline and persist result
        result = ml_anomaly_service.analyze_wallet(
            db=db,
            wallet_address=clean_addr,
            txs=txs,
            case_id=effective_case_id
        )
        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        logger.error(f"ML analysis error for {clean_addr}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Public blockchain data service is currently unavailable for ML analysis."
        )
    except Exception as e:
        logger.exception(f"Unexpected error running ML anomaly detection on {clean_addr}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Forensic ML analysis failed due to an internal processing error."
        )


@router.get(
    "/ml/history/{wallet_address}",
    response_model=List[MLAnalysisHistoryItem],
    summary="Get Past ML Anomaly Scans for a Wallet"
)
def get_wallet_ml_history(
    wallet_address: str,
    limit: int = Query(10, ge=1, le=50, description="Max history records to return"),
    db: Session = Depends(get_db)
):
    """
    Returns audit history of prior machine-learning anomaly detection analyses for the specified wallet.
    """
    clean_addr = wallet_address.strip()
    val = validate_bitcoin_address(clean_addr)
    if not val["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Bitcoin address: {val['reason']}"
        )

    return ml_anomaly_service.get_analysis_history(db=db, wallet_address=clean_addr, limit=limit)


@router.get(
    "/ml/model-info",
    response_model=ModelInfo,
    summary="Get ML Anomaly Model Architecture, Hyperparameters & Evaluation Methodology"
)
def get_ml_model_info():
    """
    Provides public model metadata, hyperparameters, and evaluation methodology notes.
    Explains the unsupervised Isolation Forest approach without fabricating accuracy metrics.
    """
    return ModelInfo(
        model_name="IsolationForest",
        model_version="1.0.0",
        algorithm_type="Unsupervised Ensemble Anomaly Detection",
        n_estimators=100,
        contamination=0.10,
        random_state=42,
        framework="scikit-learn",
        evaluation_methodology=(
            "Unsupervised path length isolation heuristic (c(n) average depth) calibrated "
            "against an empirical baseline corpus (600 profiles). Does not report synthetic accuracy."
        )
    )

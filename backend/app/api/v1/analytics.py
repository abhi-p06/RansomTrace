import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.services.blockchain_service import blockchain_service
from backend.app.services.analytics_service import analytics_service
from backend.app.services.mempool_client import validate_bitcoin_address
from backend.app.schemas.analytics import WalletAnalyticsResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Wallet Behavioural Analytics"])

@router.get(
    "/wallets/{address}/analytics",
    response_model=WalletAnalyticsResponse,
    summary="Compute Forensic Behavioural Analytics & Distributions for Wallet"
)
async def get_wallet_analytics(
    address: str,
    limit: int = Query(100, ge=1, le=100, description="Max historical transactions to process"),
    db: Session = Depends(get_db)
):
    """
    Computes statistical and behavioural features from public blockchain transactions:
    - Volume over time (inflow vs. outflow)
    - Amount variance, median, min, max
    - Velocity and transaction frequency
    - Activity burst detection (rapid clustered transfers)
    - Counterparty interaction rankings
    - Amount histogram distribution
    """
    clean_addr = address.strip()
    val = validate_bitcoin_address(clean_addr)
    if not val["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Bitcoin address: {val['reason']}"
        )

    try:
        # Fetch normalized transaction history from blockchain layer
        txs = await blockchain_service.get_wallet_transactions(clean_addr, db, limit=limit)
        analytics = analytics_service.calculate_wallet_analytics(
            address=clean_addr,
            address_type=val["type"],
            txs=txs
        )
        return analytics
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        logger.error(f"Analytics calculation error for {clean_addr}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected analytics error for {clean_addr}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate behavioral analytics for the requested address."
        )

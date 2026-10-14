import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import validate_tx_hash_format
from backend.app.services.blockchain_service import blockchain_service
from backend.app.services.mempool_client import validate_bitcoin_address
from backend.app.schemas.wallet import WalletStatsResponse, TransactionResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Blockchain Forensics & Wallets"])

@router.get(
    "/wallets/{address}",
    response_model=WalletStatsResponse,
    summary="Lookup Bitcoin Wallet Address & Activity Summary"
)
async def get_wallet_info(
    address: str,
    case_id: Optional[str] = Query(None, description="Optional investigation case ID to bind wallet to"),
    db: Session = Depends(get_db)
):
    """
    Retrieves publicly available Bitcoin blockchain statistics for an address.
    Validates address format (P2PKH, P2SH, SegWit Bech32, Taproot Bech32m).
    Safely handles rate limits and upstream provider errors without exposing internals.
    """
    clean_addr = address.strip()
    val = validate_bitcoin_address(clean_addr)
    if not val["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Bitcoin address format: {val['reason']}"
        )

    try:
        data = await blockchain_service.get_wallet_overview(clean_addr, db, case_id=case_id)
        return data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        logger.error(f"Blockchain runtime error for {clean_addr}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error analyzing wallet {clean_addr}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while analyzing public blockchain data."
        )

@router.get(
    "/wallets/{address}/transactions",
    response_model=List[TransactionResponse],
    summary="Get Wallet Public Transaction History"
)
async def get_wallet_transactions(
    address: str,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Retrieves normalized Bitcoin transactions for the address with inputs, outputs,
    satoshi values, fee calculations, and flow direction (INCOMING/OUTGOING).
    """
    clean_addr = address.strip()
    val = validate_bitcoin_address(clean_addr)
    if not val["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Bitcoin address: {val['reason']}"
        )

    try:
        txs = await blockchain_service.get_wallet_transactions(clean_addr, db, limit=limit)
        return txs
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        logger.error(f"Blockchain runtime error for txs {clean_addr}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error getting txs for {clean_addr}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while parsing transaction history."
        )

@router.get(
    "/transactions/{txid}",
    response_model=TransactionResponse,
    summary="Lookup Public Bitcoin Transaction by TXID"
)
async def get_transaction(txid: str, db: Session = Depends(get_db)):
    """
    Retrieves detailed public Bitcoin transaction information by 64-char transaction hash (TXID).
    """
    clean_txid = txid.strip()
    if not validate_tx_hash_format(clean_txid):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction hash format. TXID must be an exact 64-character hexadecimal string."
        )

    try:
        data = await blockchain_service.get_transaction_details(clean_txid, db)
        return data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bitcoin transaction '{clean_txid}' was not found on the public blockchain."
        )
    except RuntimeError as e:
        logger.error(f"Blockchain runtime error for {clean_txid}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Upstream blockchain provider is currently unreachable."
        )
    except Exception as e:
        logger.error(f"Unexpected error for tx {clean_txid}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process public transaction lookup."
        )

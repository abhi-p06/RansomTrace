import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.services.graph_service import graph_service
from backend.app.services.mempool_client import validate_bitcoin_address
from backend.app.schemas.graph import FundFlowGraphResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Cryptocurrency Fund Flow Graph"])

@router.get(
    "/wallets/{address}/graph",
    response_model=FundFlowGraphResponse,
    summary="Construct Directed Fund Flow Topology Graph (NetworkX)"
)
async def get_wallet_fund_flow_graph(
    address: str,
    depth: int = Query(1, ge=1, le=3, description="Graph traversal depth (1=Direct, 2=Extended, 3=Deep network)"),
    max_nodes: int = Query(50, ge=10, le=100, description="Maximum graph nodes safety limit"),
    db: Session = Depends(get_db)
):
    """
    Builds a directed cryptocurrency fund-flow graph where:
    - NODE = Public Bitcoin Wallet / Address
    - EDGE = Transaction / Satoshi flow with TXID, amount, and timestamp

    Calculates NetworkX topological metrics (density, degree centrality, hub detection).
    Enforces configurable traversal depth (1 to 3 hops) with safety bounds to prevent infinite queries.
    """
    clean_addr = address.strip()
    val = validate_bitcoin_address(clean_addr)
    if not val["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Bitcoin address: {val['reason']}"
        )

    try:
        graph_data = await graph_service.build_fund_flow_graph(
            target_address=clean_addr,
            db=db,
            depth=depth,
            max_nodes=max_nodes
        )
        return graph_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        logger.error(f"Graph construction error for {clean_addr}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected graph error for {clean_addr}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate cryptocurrency fund-flow graph."
        )

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.services.dashboard_service import dashboard_service
from backend.app.schemas.dashboard import DashboardStatsResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Investigation Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardStatsResponse,
    summary="Get SOC Command Center Dashboard Summary & Investigation Metrics"
)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Returns aggregated real-time operational statistics for the primary SOC command dashboard,
    including active cases, analyzed wallets, transaction volume, preserved evidence,
    risk tier distribution, and chronological investigation timeline.
    """
    return dashboard_service.get_dashboard_summary(db)

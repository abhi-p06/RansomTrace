from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.database import get_db, check_db_connection
from backend.app.schemas.health import HealthResponse, DatabaseHealth

router = APIRouter()

@router.get("/health", response_model=HealthResponse, summary="System Health & Subsystem Status")
def get_health_status(db: Session = Depends(get_db)):
    """
    Returns system diagnostic status, database connectivity verification,
    and platform environment information.
    """
    db_check = check_db_connection()

    return HealthResponse(
        project=settings.PROJECT_NAME,
        version=settings.VERSION,
        status="operational" if db_check["status"] == "connected" else "degraded",
        environment=settings.ENVIRONMENT,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        database=DatabaseHealth(
            status=db_check["status"],
            dialect=db_check["dialect"],
            detail=db_check["detail"]
        ),
        modules={
            "api_gateway": "ready",
            "database_session": "active",
            "evidence_vault": "initialized"
        }
    )

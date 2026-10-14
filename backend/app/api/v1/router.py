from fastapi import APIRouter
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.cases import router as cases_router
from backend.app.api.v1.wallets import router as wallets_router
from backend.app.api.v1.analytics import router as analytics_router
from backend.app.api.v1.graph import router as graph_router
from backend.app.api.v1.ml import router as ml_router
from backend.app.api.v1.risk import router as risk_router
from backend.app.api.v1.evidence import router as evidence_router
from backend.app.api.v1.reports import router as reports_router
from backend.app.api.v1.dashboard import router as dashboard_router

api_router = APIRouter()

# Core system routes
api_router.include_router(health_router, tags=["System Health"])

# Investigation Dashboard & Global SOC Metrics
api_router.include_router(dashboard_router)

# Forensic Investigation Cases
api_router.include_router(cases_router)

# Blockchain Forensics & Public Bitcoin Ledger
api_router.include_router(wallets_router)

# Wallet Behavioural Analytics & Distributions
api_router.include_router(analytics_router)

# Cryptocurrency Fund Flow Graph
api_router.include_router(graph_router)

# Forensic Machine Learning & Anomaly Detection
api_router.include_router(ml_router)

# Hybrid Investigative Risk Scoring
api_router.include_router(risk_router)

# Digital Forensics, Evidence Locker & Chain of Custody
api_router.include_router(evidence_router)

# Forensic PDF Reports
api_router.include_router(reports_router)




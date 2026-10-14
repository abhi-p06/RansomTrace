from contextlib import asynccontextmanager
import os
import uuid
import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from backend.app.core.config import settings
from backend.app.core.database import Base, engine, check_db_connection
from backend.app.core.security import (
    SecurityHeadersMiddleware,
    RateLimiterMiddleware,
    RequestSizeLimitMiddleware,
)
from backend.app.api.v1.router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ransomtrace")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure evidence vault directory exists & verify DB schema
    logger.info("Initializing RansomTrace platform...")
    os.makedirs(settings.EVIDENCE_VAULT_DIR, exist_ok=True)
    from backend.app.services.data_layer import init_database, load_demo_data
    from backend.app.core.database import SessionLocal
    init_database()
    db_session = SessionLocal()
    try:
        load_demo_data(db_session, force_reload=False)
        logger.info("Synthetic demo dataset verified and ready.")
    except Exception as e:
        logger.warning(f"Demo data initialization notice: {e}")
    finally:
        db_session.close()

    db_status = check_db_connection()
    logger.info(f"Database status: {db_status['status']} (Dialect: {db_status['dialect']})")
    yield
    # Shutdown
    logger.info("Shutting down RansomTrace platform.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# 1. Payload Size Limit Middleware (Prevents DoS via memory exhaustion)
app.add_middleware(RequestSizeLimitMiddleware, max_bytes=10 * 1024 * 1024)

# 2. Rate Limiting Middleware (Sliding window per client IP)
app.add_middleware(RateLimiterMiddleware, max_requests_per_minute=2000)

# 3. Security Headers Middleware (OWASP recommended defense-in-depth)
app.add_middleware(SecurityHeadersMiddleware)

# 4. CORS Middleware (Restricted methods and explicit origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
)

# Global Safe Error Handlers (Prevents stack trace / internal code leakage)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Returns clean, sanitized validation error messages without leaking internal tracebacks."""
    errors = []
    for err in exc.errors():
        field = " -> ".join([str(loc) for loc in err.get("loc", [])])
        msg = err.get("msg", "Invalid input value")
        errors.append({"field": field, "message": msg})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": "One or more input parameters failed forensic validation checks.",
            "fields": errors,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Catches all unexpected internal exceptions, logs with an opaque UUID4 tracking ID,
    and returns a safe generic response without exposing stack traces to the client.
    """
    error_id = str(uuid.uuid4())
    logger.exception(f"Unhandled system error [ID: {error_id}] on {request.method} {request.url.path}: {exc}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "error_id": error_id,
            "message": "An unexpected error occurred while processing the forensic request. The incident has been recorded for review.",
        },
    )


# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
def root_status():
    """Platform identity and discovery endpoint."""
    return {
        "platform": settings.PROJECT_NAME,
        "description": settings.PROJECT_DESCRIPTION,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "health_check": f"{settings.API_V1_STR}/health",
    }


@app.get("/health", tags=["Root"])
def root_health():
    """Convenience alias for /api/v1/health."""
    db_check = check_db_connection()
    return {
        "project": settings.PROJECT_NAME,
        "status": "operational" if db_check["status"] == "connected" else "degraded",
        "database": db_check,
    }

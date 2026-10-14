import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Configure engine based on dialect
connect_args = {}
engine_kwargs = {}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
    })

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator:
    """FastAPI dependency for obtaining a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_connection() -> dict:
    """Verifies active connectivity to the database."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar()
            dialect = engine.dialect.name
            return {
                "status": "connected",
                "dialect": dialect,
                "detail": f"Active connection verified (SELECT 1 -> {result})"
            }
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return {
            "status": "error",
            "dialect": engine.dialect.name if hasattr(engine, "dialect") else "unknown",
            "detail": str(e)
        }

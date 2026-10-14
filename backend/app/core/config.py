import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from pathlib import Path

_DEFAULT_DB_PATH = (Path(__file__).resolve().parent.parent.parent / "ransomtrace.db").as_posix()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    PROJECT_NAME: str = "RansomTrace"
    PROJECT_DESCRIPTION: str = "Cybercrime Investigation, Cryptocurrency Forensics & AI-Based Ransomware Payment Analysis Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database: Defaults to SQLite for immediate zero-config execution,
    # and automatically connects to PostgreSQL when DATABASE_URL is configured.
    DATABASE_URL: str = f"sqlite:///{_DEFAULT_DB_PATH}"

    # CORS settings (accepts comma-separated string or JSON array)
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ]

    # Blockchain Provider API
    MEMPOOL_API_BASE: str = "https://mempool.space/api"
    HTTP_TIMEOUT_SECONDS: int = 15

    # Forensic Evidence Storage
    EVIDENCE_VAULT_DIR: str = "./data/evidence_vault"

    # Hybrid Risk Scoring Configuration
    RISK_RULE_WEIGHT: float = 0.50
    RISK_ML_WEIGHT: float = 0.50

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v_stripped = v.strip()
            if v_stripped.startswith("[") and v_stripped.endswith("]"):
                try:
                    return json.loads(v_stripped)
                except Exception:
                    pass
            return [i.strip() for i in v_stripped.split(",") if i.strip()]
        return v

settings = Settings()

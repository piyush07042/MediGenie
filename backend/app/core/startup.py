"""
Startup validation and shared application state.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.db.session import SessionLocal
from ml.registry import resolve_model_directory


@dataclass
class AppState:
    """Shared runtime state for the backend application."""

    supervisor: Any = None
    ml_model: Any = None
    vector_store: Any = None
    ocr_engine: Any = None


app_state = AppState()


def validate_environment() -> None:
    """
    Validate required configuration at startup.
    """
    _validate_required_settings()
    _validate_directories()
    _validate_database_connection()
    _validate_heart_disease_model_path()


ROOT_DIR = Path(__file__).resolve().parents[2]


def _resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT_DIR / path


def _ensure_directory(path: Path) -> Path:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise RuntimeError(
            f"Cannot create required directory '{path}': {exc}"
        ) from exc

    if not path.exists() or not path.is_dir():
        raise RuntimeError(f"Required directory '{path}' is not available.")

    return path


def _validate_required_settings() -> None:
    if not settings.SECRET_KEY:
        raise RuntimeError("SECRET_KEY must be configured.")
    if not settings.DATABASE_URL:
        raise RuntimeError("DATABASE_URL must be configured.")


def _validate_directories() -> None:
    _ensure_directory(_resolve_path(settings.UPLOAD_DIRECTORY))
    _ensure_directory(_resolve_path(settings.LOG_DIRECTORY))
    _ensure_directory(_resolve_path(settings.RAG_DB_DIRECTORY))


def _validate_database_connection() -> None:
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
    except Exception as exc:
        raise RuntimeError(
            f"Unable to connect to database: {exc}"
        ) from exc
    finally:
        try:
            db.close()
        except Exception:
            logging.warning("Failed to close database session during startup validation.")


def _validate_heart_disease_model_path() -> None:
    model_path = resolve_model_directory("heart_disease")
    if not model_path.exists() or not model_path.is_dir():
        raise RuntimeError(
            f"Heart disease model directory not found: {model_path}"
        )

    if not any(
        (model_path / filename).exists()
        for filename in ["model.joblib", "model.json", "schema.json"]
    ):
        raise RuntimeError(
            f"Heart disease model directory is missing required artifacts: {model_path}"
        )
        # Register model path in global app state for health checks
        from app.core.startup import app_state as _app_state  # local import to avoid cycles
        try:
            _app_state.ml_model = str(model_path)
        except Exception:
            pass
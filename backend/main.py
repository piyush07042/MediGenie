"""
MediGenie FastAPI Application
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api.routes import api_router
from app.core.config import settings
from app.core.compression import configure_compression
from app.core.cors import configure_cors
from app.core.logging import RequestIDMiddleware, configure_logging
from app.core.metrics import configure_metrics
from app.core.startup import validate_environment, app_state
from app.core.security_headers import configure_security_headers
from app.core.rag import seed_sample_guidelines
from app.db.session import create_database
from app.core.scheduler import start_scheduler, shutdown_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup/shutdown lifecycle.
    """

    try:
        configure_logging()
        validate_environment()
        create_database()
        try:
            seed_sample_guidelines()
            app_state.vector_store = True
        except Exception as exc:
            logging.warning("Vector store initialization skipped: %s", exc)
            app_state.vector_store = None
        # Start in-app scheduler if configured
        try:
            if settings.SCHEDULER_ENABLED and settings.SCHEDULER_INTERVAL_SECONDS > 0:
                start_scheduler(app)
        except Exception as exc:
            logging.warning("Scheduler failed to start: %s", exc)
    except asyncio.CancelledError:
        raise
    except Exception:
        app.state.startup_error = True
        app.state.startup_error_details = "startup initialization failed"

    try:
        yield
    except asyncio.CancelledError:
        return
    except Exception:
        raise
    finally:
        # Ensure scheduler is shutdown on application stop
        try:
            shutdown_scheduler()
        except Exception:
            logging.exception("Error shutting down scheduler during app shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Multi-Agent Clinical Decision Support System",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.state.startup_error = False
app.state.startup_error_details = None

app.add_middleware(RequestIDMiddleware)
configure_cors(app)
configure_security_headers(app)
configure_compression(app)
configure_metrics(app)

@app.get("/")
def root():
    return RedirectResponse(url=f"{settings.API_V1_PREFIX}/health")

app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)
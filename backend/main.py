"""
MediGenie FastAPI Application
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
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
from app.db.session import create_database, test_connection, get_masked_database_url
from app.core.scheduler import start_scheduler, shutdown_scheduler
from app.api.health import health_check, readiness_probe, liveness_probe
from app.core.logging import get_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup/shutdown lifecycle.
    """

    startup_success = False
    try:
        configure_logging()
        validate_environment()
        # Print masked DB URL and validate connectivity early so the app fails fast
        logger = get_logger("app.startup")
        try:
            masked = get_masked_database_url()
            logger.info("Resolved DATABASE_URL: %s", masked)
        except Exception:
            logger.exception("Failed to resolve DATABASE_URL for logging")

        try:
            test_connection()
        except Exception as exc:
            # Raise to make startup fail immediately with logged exception
            logger.exception("Database connectivity check failed during startup")
            raise

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
        # Log registered routes after routers are included and logging configured
        try:
            _log_routes()
        except Exception:
            logging.exception("Failed to list routes during startup")
        
        # Mark startup as successful - all critical initialization completed
        startup_success = True
        app.state.startup_error = False
        app.state.startup_error_details = None
        logger = get_logger("app.startup")
        logger.info("Application startup completed successfully")
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        logger = get_logger("app.startup")
        logger.exception("Application startup failed")
        app.state.startup_error = True
        app.state.startup_error_details = str(exc) or "startup initialization failed"
        raise

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


def _log_routes():
    logger = get_logger("app.startup")
    logger.info("Registered routes:")
    for route in app.routes:
        methods = ",".join(sorted(route.methods)) if getattr(route, "methods", None) else ""
        logger.info("  %s  %s %s", methods, getattr(route, "name", ""), getattr(route, "path", ""))


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

# Expose health endpoints at root as well as under API prefix
@app.get("/health")
async def _health_root():
    return await health_check()


@app.get("/ready")
async def _ready_root(request: Request):
    return await readiness_probe(request)


@app.get("/live")
async def _live_root():
    return await liveness_probe()


# Print route list at startup (will run when logging configured during lifespan)
# Route listing is logged during lifespan startup
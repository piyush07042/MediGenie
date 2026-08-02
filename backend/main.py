"""
MediGenie FastAPI Application
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import api_router
from app.core.config import settings
from app.core.compression import configure_compression
from app.core.cors import configure_cors
from app.core.logging import configure_logging
from app.core.startup import validate_environment
from app.core.security_headers import configure_security_headers
from app.db.session import create_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup/shutdown lifecycle.
    """

    try:
        configure_logging()
        validate_environment()
        create_database()
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


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Multi-Agent Clinical Decision Support System",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

configure_cors(app)
configure_security_headers(app)
configure_compression(app)

app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)
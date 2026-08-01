"""
Central API Router

Registers all API modules for MediGenie.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.clinical import router as clinical_router
from app.api.endpoints import router as endpoints_router
from app.api.fhir import router as fhir_router
from app.api.health import router as health_router
from app.api.patients import router as patients_router
from app.api.reporting import router as reporting_router
from app.api.upload import router as upload_router
from app.api.version import router as version_router

api_router = APIRouter()

# =====================================================
# Authentication
# =====================================================

api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"],
)

# =====================================================
# Patient Management
# =====================================================

api_router.include_router(
    patients_router,
    prefix="/patients",
    tags=["Patients"],
)

# =====================================================
# Clinical Decision Support
# =====================================================

api_router.include_router(
    clinical_router,
    tags=["Clinical Decision Support"],
)

# =====================================================
# Medical Report Upload
# =====================================================

api_router.include_router(
    upload_router,
)

# =====================================================
# Clinical Reporting
# =====================================================

api_router.include_router(
    reporting_router,
)

# =====================================================
# FHIR Export
# =====================================================

api_router.include_router(
    fhir_router,
)

# =====================================================
# AI Clinical Chat
# =====================================================

api_router.include_router(
    chat_router,
)

# =====================================================
# Health & Monitoring
# =====================================================

api_router.include_router(
    health_router,
)

api_router.include_router(
    version_router,
)

# =====================================================
# Miscellaneous / General Endpoints
# =====================================================

api_router.include_router(
    endpoints_router,
    tags=["General"],
)
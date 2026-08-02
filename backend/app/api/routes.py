"""
Central API Router

Registers all API modules for MediGenie.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.auth import router as auth_router
try:
    from app.api.chat import router as chat_router
except Exception:
    chat_router = None
try:
    from app.api.clinical import router as clinical_router
except Exception:
    clinical_router = None
try:
    from app.api.fhir import router as fhir_router
except Exception:
    fhir_router = None
try:
    from app.api.clinical import router as clinical_router
except Exception:
    clinical_router = None
try:
    from app.api.fhir import router as fhir_router
except Exception:
    fhir_router = None
from app.api.health import router as health_router
try:
    from app.api.patients import router as patients_router
except Exception:
    patients_router = None
try:
    from app.api.reporting import router as reporting_router
except Exception:
    reporting_router = None
try:
    from app.api.upload import router as upload_router
except Exception:
    upload_router = None
from app.api.version import router as version_router
try:
    from app.api.endpoints import router as endpoints_router
except Exception:
    endpoints_router = None

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

if patients_router:
    api_router.include_router(
        patients_router,
        prefix="/patients",
        tags=["Patients"],
    )

# =====================================================
# Clinical Decision Support
# =====================================================

if clinical_router:
    api_router.include_router(
        clinical_router,
        tags=["Clinical Decision Support"],
    )

# =====================================================
# Medical Report Upload
# =====================================================

if upload_router:
    api_router.include_router(
        upload_router,
    )

# =====================================================
# Clinical Reporting
# =====================================================

if reporting_router:
    api_router.include_router(
        reporting_router,
    )

# =====================================================
# FHIR Export
# =====================================================

if fhir_router:
    api_router.include_router(
        fhir_router,
    )

# =====================================================
# AI Clinical Chat
# =====================================================

if chat_router:
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

if endpoints_router:
    api_router.include_router(
        endpoints_router,
        tags=["General"],
    )
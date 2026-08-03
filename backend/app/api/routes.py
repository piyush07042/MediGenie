"""
Central API Router

Registers all API modules for MediGenie.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.clinical import router as clinical_router
from app.api.diagnostics import router as diagnostics_router
from app.api.drug_safety import router as drug_safety_router
from app.api.endpoints import router as endpoints_router
from app.api.fhir import router as fhir_router
from app.api.health import router as health_router
from app.api.knowledge import router as knowledge_router
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
)

# =====================================================
# Patient Management
# =====================================================

api_router.include_router(patients_router)

# =====================================================
# Clinical Decision Support
# =====================================================

api_router.include_router(clinical_router)

# =====================================================
# Medical Report Upload
# =====================================================

api_router.include_router(upload_router)

# =====================================================
# Clinical Reporting
# =====================================================

api_router.include_router(reporting_router)

# =====================================================
# Drug Safety API
# =====================================================
api_router.include_router(drug_safety_router)

# =====================================================
# Knowledge / RAG indexing
# =====================================================
api_router.include_router(knowledge_router)

# =====================================================
# FHIR Export
# =====================================================

api_router.include_router(fhir_router)

# =====================================================
# AI Clinical Chat
# =====================================================

api_router.include_router(chat_router)

# =====================================================
# Health & Monitoring
# =====================================================

api_router.include_router(
    health_router,
)

api_router.include_router(
    version_router,
)
api_router.include_router(diagnostics_router, prefix="/diagnostics")

# =====================================================
# Miscellaneous / General Endpoints
# =====================================================

api_router.include_router(
    endpoints_router,
    tags=["General"],
)
"""
Patient Management API
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.models import Patient, User
from app.schemas.common import ApiResponse
from app.schemas.schemas import (
    PatientCreate,
    PatientResponse,
)

router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


@router.post(
    "/",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_patient(
    patient_in: PatientCreate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    patient = Patient(
        doctor_id=current_user.id,
        **patient_in.model_dump(),
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    return ApiResponse(
        message="Patient created successfully.",
        data=PatientResponse.model_validate(
            patient
        ),
    )


@router.get(
    "/",
    response_model=ApiResponse,
)
def list_patients(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    patients = (
        db.query(Patient)
        .filter(
            Patient.doctor_id
            == current_user.id
        )
        .all()
    )

    return ApiResponse(
        message="Patients retrieved successfully.",
        data=[
            PatientResponse.model_validate(p)
            for p in patients
        ],
    )
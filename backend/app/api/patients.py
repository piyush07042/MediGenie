from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.models import Patient, User
from app.schemas.schemas import PatientCreate, PatientResponse
from app.core.deps import get_current_user

router = APIRouter(prefix="/patients", tags=["Patient Management"])

@router.post("/", response_model=PatientResponse)
def create_patient(
    patient_in: PatientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_patient = Patient(
        doctor_id=current_user.id,
        **patient_in.model_dump()
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

@router.get("/", response_model=List[PatientResponse])
def get_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Fetch only patients belonging to the logged-in doctor
    return db.query(Patient).filter(Patient.doctor_id == current_user.id).all()
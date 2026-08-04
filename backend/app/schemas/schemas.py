from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.models import UserRole

# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.DOCTOR

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    success: bool = True
    message: str
    data: Token | None = None

# Patient Schemas
class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    age: int
    gender: str
    medical_history: Optional[Dict[str, Any]] = {}
    allergies: Optional[List[str]] = []
    current_medications: Optional[List[str]] = []

class PatientResponse(PatientCreate):
    id: int
    doctor_id: int
    created_at: datetime

    class Config:
        from_attributes = True
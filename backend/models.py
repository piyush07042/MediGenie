from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class PatientRecord(Base):
    __tablename__ = "patient_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, index=True, default="PT-UNKNOWN")
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    glucose = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)
    systolic_bp = Column(Float, nullable=True)
    cholesterol = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship to clinical summaries
    summaries = relationship("ClinicalSummary", back_populates="patient")


class ClinicalSummary(Base):
    __tablename__ = "clinical_summaries"

    id = Column(Integer, primary_key=True, index=True)
    patient_record_id = Column(Integer, ForeignKey("patient_records.id"))
    status = Column(String)  # 'success' or 'fallback_success'
    risk_score = Column(Float, nullable=True)
    risk_category = Column(String, nullable=True)
    summary_text = Column(Text)
    raw_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    patient = relationship("PatientRecord", back_populates="summaries")
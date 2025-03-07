import enum
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Text, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from app.db.database import Base

class RoleType(str, enum.Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleType), nullable=False)
    department = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    predictions = relationship("SepsisPrediction", back_populates="user")
    feedback = relationship("Feedback", back_populates="user")

class Patient(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True, index=True)  # Using FHIR Resource ID
    fhir_resource = Column(JSON, nullable=True)  # Storing the complete FHIR Patient resource
    mrn = Column(String, index=True, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    clinical_data = relationship("ClinicalData", back_populates="patient")
    predictions = relationship("SepsisPrediction", back_populates="patient")
    alerts = relationship("Alert", back_populates="patient")

class ClinicalData(Base):
    __tablename__ = "clinical_data"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"))
    fhir_resource_id = Column(String, index=True, nullable=True)
    fhir_resource_type = Column(String, nullable=True)
    fhir_resource = Column(JSON, nullable=True)  # Storing the complete FHIR resource
    timestamp = Column(DateTime(timezone=True), nullable=False)
    
    # Common vital signs and lab values used for sepsis prediction
    heart_rate = Column(Float, nullable=True)
    respiratory_rate = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    systolic_bp = Column(Float, nullable=True)
    diastolic_bp = Column(Float, nullable=True)
    oxygen_saturation = Column(Float, nullable=True)
    blood_glucose = Column(Float, nullable=True)
    wbc_count = Column(Float, nullable=True)
    platelet_count = Column(Float, nullable=True)
    lactate = Column(Float, nullable=True)
    creatinine = Column(Float, nullable=True)
    bilirubin = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="clinical_data")

class AlertStatus(str, enum.Enum):
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    ACTION_TAKEN = "action_taken"
    DISMISSED = "dismissed"

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"))
    prediction_id = Column(String, ForeignKey("sepsis_predictions.id"))
    alert_type = Column(String, nullable=False)
    severity = Column(Integer, nullable=False)  # 1-5 scale, 5 being most severe
    status = Column(Enum(AlertStatus), default=AlertStatus.PENDING)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by = Column(String, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="alerts")
    prediction = relationship("SepsisPrediction", back_populates="alerts")

class SepsisPrediction(Base):
    __tablename__ = "sepsis_predictions"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # User who requested prediction
    probability = Column(Float, nullable=False)
    is_sepsis_risk = Column(Boolean, nullable=False)
    features_used = Column(JSON, nullable=True)
    model_version = Column(String, nullable=False)
    explanation = Column(JSON, nullable=True)  # SHAP values or other explanation data
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="predictions")
    user = relationship("User", back_populates="predictions")
    alerts = relationship("Alert", back_populates="prediction")
    feedback = relationship("Feedback", back_populates="prediction")

class FeedbackType(str, enum.Enum):
    CORRECT = "correct"
    FALSE_POSITIVE = "false_positive"
    FALSE_NEGATIVE = "false_negative"
    UNSURE = "unsure"

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    prediction_id = Column(String, ForeignKey("sepsis_predictions.id"))
    user_id = Column(String, ForeignKey("users.id"))
    feedback_type = Column(Enum(FeedbackType), nullable=False)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    prediction = relationship("SepsisPrediction", back_populates="feedback")
    user = relationship("User", back_populates="feedback")
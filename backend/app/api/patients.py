from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import crud
from app.db.database import get_db
from app.db.models import User
from app.core.security import get_current_active_user
from app.services.patient_service import PatientService
from pydantic import BaseModel, Field

router = APIRouter()
patient_service = PatientService()

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    mrn: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: str
    created_at: str
    updated_at: Optional[str] = None

class PatientSummary(BaseModel):
    patient: Dict[str, Any]
    latest_vitals: Dict[str, Any]
    recent_clinical_data: List[Dict[str, Any]]
    sepsis_predictions: List[Dict[str, Any]]
    latest_prediction: Optional[Dict[str, Any]] = None
    active_alerts: List[Dict[str, Any]]
    alert_count: int

@router.get("/", response_model=List[PatientResponse])
async def get_patients(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get list of patients with pagination
    """
    patients = crud.get_patients(db, skip=skip, limit=limit)
    return [
        {
            "id": patient.id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
            "gender": patient.gender,
            "mrn": patient.mrn,
            "phone_number": patient.phone_number,
            "email": patient.email,
            "address": patient.address,
            "created_at": patient.created_at.isoformat() if patient.created_at else None,
            "updated_at": patient.updated_at.isoformat() if patient.updated_at else None
        }
        for patient in patients
    ]

@router.post("/", response_model=PatientResponse)
async def create_patient(
    patient_data: PatientCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create a new patient
    """
    # Check if patient with same MRN exists
    if patient_data.mrn:
        existing_patient = crud.get_patient_by_mrn(db, patient_data.mrn)
        if existing_patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Patient with MRN {patient_data.mrn} already exists"
            )
    
    # Create patient
    patient_dict = patient_data.dict()
    new_patient = crud.create_patient(db, patient_dict)
    
    return {
        "id": new_patient.id,
        "first_name": new_patient.first_name,
        "last_name": new_patient.last_name,
        "date_of_birth": new_patient.date_of_birth.isoformat() if new_patient.date_of_birth else None,
        "gender": new_patient.gender,
        "mrn": new_patient.mrn,
        "phone_number": new_patient.phone_number,
        "email": new_patient.email,
        "address": new_patient.address,
        "created_at": new_patient.created_at.isoformat() if new_patient.created_at else None,
        "updated_at": new_patient.updated_at.isoformat() if new_patient.updated_at else None
    }

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get a specific patient by ID
    """
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    
    return {
        "id": patient.id,
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
        "gender": patient.gender,
        "mrn": patient.mrn,
        "phone_number": patient.phone_number,
        "email": patient.email,
        "address": patient.address,
        "created_at": patient.created_at.isoformat() if patient.created_at else None,
        "updated_at": patient.updated_at.isoformat() if patient.updated_at else None
    }

@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    patient_data: PatientCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update a patient's information
    """
    # Check if patient exists
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    
    # Update patient
    patient_dict = patient_data.dict()
    updated_patient = crud.update_patient(db, patient_id, patient_dict)
    
    return {
        "id": updated_patient.id,
        "first_name": updated_patient.first_name,
        "last_name": updated_patient.last_name,
        "date_of_birth": updated_patient.date_of_birth.isoformat() if updated_patient.date_of_birth else None,
        "gender": updated_patient.gender,
        "mrn": updated_patient.mrn,
        "phone_number": updated_patient.phone_number,
        "email": updated_patient.email,
        "address": updated_patient.address,
        "created_at": updated_patient.created_at.isoformat() if updated_patient.created_at else None,
        "updated_at": updated_patient.updated_at.isoformat() if updated_patient.updated_at else None
    }

@router.get("/{patient_id}/summary", response_model=PatientSummary)
async def get_patient_summary(
    patient_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get a comprehensive summary of patient data including clinical data and predictions
    """
    summary = await patient_service.get_patient_summary(db, patient_id)
    if "status" in summary and summary["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=summary["message"]
        )
    
    return summary

@router.get("/{patient_id}/clinical-data", response_model=List[Dict[str, Any]])
async def get_patient_clinical_data(
    patient_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get clinical data for a specific patient
    """
    # Check if patient exists
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    
    # Get clinical data
    clinical_data = crud.get_patient_clinical_data(db, patient_id, skip=skip, limit=limit)
    
    return [
        {
            "id": data.id,
            "patient_id": data.patient_id,
            "timestamp": data.timestamp.isoformat() if data.timestamp else None,
            "heart_rate": data.heart_rate,
            "respiratory_rate": data.respiratory_rate,
            "temperature": data.temperature,
            "systolic_bp": data.systolic_bp,
            "diastolic_bp": data.diastolic_bp,
            "oxygen_saturation": data.oxygen_saturation,
            "blood_glucose": data.blood_glucose,
            "wbc_count": data.wbc_count,
            "platelet_count": data.platelet_count,
            "lactate": data.lactate,
            "creatinine": data.creatinine,
            "bilirubin": data.bilirubin,
            "created_at": data.created_at.isoformat() if data.created_at else None
        }
        for data in clinical_data
    ]

@router.post("/{patient_id}/sync-fhir", response_model=Dict[str, Any])
async def sync_patient_from_fhir(
    patient_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Sync patient data from FHIR server
    """
    result = await patient_service.sync_patient_from_fhir(db, patient_id)
    if "status" in result and result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    return result

@router.get("/search/", response_model=List[Dict[str, Any]])
async def search_patients(
    query: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Search for patients by name, MRN, etc.
    """
    results = await patient_service.search_patients(db, query, limit=limit)
    return results
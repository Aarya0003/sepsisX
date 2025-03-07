from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session

from app.db import crud
from app.db.database import get_db
from app.db.models import User
from app.core.security import get_current_active_user
from app.services.prediction_service import PredictionService
from pydantic import BaseModel, Field

router = APIRouter()
prediction_service = PredictionService()

class PredictionResponse(BaseModel):
    prediction_id: str
    patient: Dict[str, Any]
    prediction: Dict[str, Any]
    timestamp: str

class BatchPredictionRequest(BaseModel):
    patient_ids: List[str] = Field(..., min_items=1, max_items=100)

class BatchPredictionResponse(BaseModel):
    successful: List[Dict[str, Any]]
    failed: List[Dict[str, Any]]
    total: int
    success_count: int
    failure_count: int

@router.post("/predict-sepsis/{patient_id}", response_model=PredictionResponse)
async def predict_sepsis_for_patient(
    patient_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Run sepsis prediction for a specific patient
    """
    # Check if patient exists
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    
    # Run prediction
    result = await prediction_service.predict_sepsis_for_patient(
        db, patient_id, current_user.id
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return result

@router.post("/batch-predict", response_model=BatchPredictionResponse)
async def batch_predict_sepsis(
    request: BatchPredictionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Run sepsis prediction for multiple patients
    """
    results = await prediction_service.batch_predict_sepsis(
        db, request.patient_ids, current_user.id
    )
    return results

@router.get("/history/{patient_id}", response_model=List[Dict[str, Any]])
async def get_prediction_history(
    patient_id: str,
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get prediction history for a specific patient
    """
    # Check if patient exists
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    
    # Get predictions
    predictions = crud.get_patient_predictions(db, patient_id, skip=skip, limit=limit)
    
    return [
        {
            "id": pred.id,
            "patient_id": pred.patient_id,
            "probability": pred.probability,
            "is_sepsis_risk": pred.is_sepsis_risk,
            "model_version": pred.model_version,
            "timestamp": pred.timestamp.isoformat() if pred.timestamp else None,
            "features_used": pred.features_used,
            "explanation": pred.explanation
        }
        for pred in predictions
    ]

@router.get("/{prediction_id}", response_model=Dict[str, Any])
async def get_prediction_details(
    prediction_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get details for a specific prediction
    """
    prediction = crud.get_prediction(db, prediction_id)
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction {prediction_id} not found"
        )
    
    # Get patient data
    patient = crud.get_patient(db, prediction.patient_id)
    
    return {
        "id": prediction.id,
        "patient_id": prediction.patient_id,
        "patient": {
            "id": patient.id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "mrn": patient.mrn
        } if patient else None,
        "probability": prediction.probability,
        "is_sepsis_risk": prediction.is_sepsis_risk,
        "model_version": prediction.model_version,
        "timestamp": prediction.timestamp.isoformat() if prediction.timestamp else None,
        "features_used": prediction.features_used,
        "explanation": prediction.explanation
    }
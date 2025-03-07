from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import crud
from app.db.database import get_db
from app.db.models import User, AlertStatus
from app.core.security import get_current_active_user
from app.services.notification import NotificationService
from pydantic import BaseModel, Field

router = APIRouter()
notification_service = NotificationService()

class AlertStatusUpdate(BaseModel):
    status: AlertStatus

class AlertResponse(BaseModel):
    id: str
    patient_id: str
    prediction_id: str
    alert_type: str
    severity: int
    status: str
    message: str
    created_at: str
    acknowledged_at: Optional[str] = None
    acknowledged_by: Optional[str] = None
    patient: Optional[Dict[str, Any]] = None

@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    status: Optional[AlertStatus] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all alerts with optional filtering by status
    """
    # Query alerts
    if status:
        alerts = db.query(crud.Alert).filter(
            crud.Alert.status == status
        ).order_by(crud.Alert.created_at.desc()).offset(skip).limit(limit).all()
    else:
        alerts = db.query(crud.Alert).order_by(
            crud.Alert.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    # Format response
    result = []
    for alert in alerts:
        # Get patient data
        patient = crud.get_patient(db, alert.patient_id)
        patient_data = None
        if patient:
            patient_data = {
                "id": patient.id,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "mrn": patient.mrn
            }
        
        result.append({
            "id": alert.id,
            "patient_id": alert.patient_id,
            "prediction_id": alert.prediction_id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "status": alert.status,
            "message": alert.message,
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
            "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
            "acknowledged_by": alert.acknowledged_by,
            "patient": patient_data
        })
    
    return result

@router.get("/pending", response_model=List[AlertResponse])
async def get_pending_alerts(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all pending (unacknowledged) alerts
    """
    alerts = crud.get_pending_alerts(db, skip=skip, limit=limit)
    
    # Format response
    result = []
    for alert in alerts:
        # Get patient data
        patient = crud.get_patient(db, alert.patient_id)
        patient_data = None
        if patient:
            patient_data = {
                "id": patient.id,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "mrn": patient.mrn
            }
        
        result.append({
            "id": alert.id,
            "patient_id": alert.patient_id,
            "prediction_id": alert.prediction_id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "status": alert.status,
            "message": alert.message,
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
            "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
            "acknowledged_by": alert.acknowledged_by,
            "patient": patient_data
        })
    
    return result

@router.get("/patient/{patient_id}", response_model=List[AlertResponse])
async def get_patient_alerts(
    patient_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get alerts for a specific patient
    """
    # Check if patient exists
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    
    # Get alerts
    alerts = crud.get_patient_alerts(db, patient_id, skip=skip, limit=limit)
    
    # Format response
    result = []
    for alert in alerts:
        result.append({
            "id": alert.id,
            "patient_id": alert.patient_id,
            "prediction_id": alert.prediction_id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "status": alert.status,
            "message": alert.message,
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
            "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
            "acknowledged_by": alert.acknowledged_by,
            "patient": {
                "id": patient.id,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "mrn": patient.mrn
            }
        })
    
    return result

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get a specific alert by ID
    """
    alert = crud.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found"
        )
    
    # Get patient data
    patient = crud.get_patient(db, alert.patient_id)
    patient_data = None
    if patient:
        patient_data = {
            "id": patient.id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "mrn": patient.mrn
        }
    
    return {
        "id": alert.id,
        "patient_id": alert.patient_id,
        "prediction_id": alert.prediction_id,
        "alert_type": alert.alert_type,
        "severity": alert.severity,
        "status": alert.status,
        "message": alert.message,
        "created_at": alert.created_at.isoformat() if alert.created_at else None,
        "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
        "acknowledged_by": alert.acknowledged_by,
        "patient": patient_data
    }

@router.put("/{alert_id}/status", response_model=AlertResponse)
async def update_alert_status(
    alert_id: str,
    status_update: AlertStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update the status of an alert (acknowledge, mark as actioned, dismiss)
    """
    # Check if alert exists
    alert = crud.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found"
        )
    
    # Update status
    updated_alert = crud.update_alert_status(
        db, alert_id, status_update.status, current_user.id
    )
    
    # Get patient data
    patient = crud.get_patient(db, updated_alert.patient_id)
    patient_data = None
    if patient:
        patient_data = {
            "id": patient.id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "mrn": patient.mrn
        }
    
    return {
        "id": updated_alert.id,
        "patient_id": updated_alert.patient_id,
        "prediction_id": updated_alert.prediction_id,
        "alert_type": updated_alert.alert_type,
        "severity": updated_alert.severity,
        "status": updated_alert.status,
        "message": updated_alert.message,
        "created_at": updated_alert.created_at.isoformat() if updated_alert.created_at else None,
        "acknowledged_at": updated_alert.acknowledged_at.isoformat() if updated_alert.acknowledged_at else None,
        "acknowledged_by": updated_alert.acknowledged_by,
        "patient": patient_data
    }

@router.post("/{alert_id}/send-notification", response_model=Dict[str, Any])
async def send_alert_notification(
    alert_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Manually send notification for an existing alert
    """
    # Check if alert exists
    alert = crud.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found"
        )
    
    # Get patient data
    patient = crud.get_patient(db, alert.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {alert.patient_id} not found"
        )
    
    # Get users to notify (only doctors and nurses)
    users = db.query(User).filter(
        User.is_active == True,
        (User.role == "doctor") | (User.role == "nurse")
    ).all()
    
    if not users:
        return {"status": "no_users", "message": "No active users to notify"}
    
    # Convert patient to dict
    patient_dict = {c.key: getattr(patient, c.key) for c in patient.__table__.columns}
    
    # Send notifications
    notification_results = await notification_service.notify_users_of_alert(
        alert, patient_dict, users
    )
    
    return {
        "status": "success",
        "alert_id": alert_id,
        "notification_results": notification_results
    }
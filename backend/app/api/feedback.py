from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import crud
from app.db.database import get_db
from app.db.models import User, FeedbackType
from app.core.security import get_current_active_user
from pydantic import BaseModel, Field

router = APIRouter()

class FeedbackCreate(BaseModel):
    prediction_id: str
    feedback_type: FeedbackType
    comments: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: str
    prediction_id: str
    user_id: str
    feedback_type: str
    comments: Optional[str] = None
    created_at: str
    user_name: Optional[str] = None

@router.post("/", response_model=FeedbackResponse)
async def create_feedback(
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Submit feedback on a sepsis prediction
    """
    # Check if prediction exists
    prediction = crud.get_prediction(db, feedback_data.prediction_id)
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction {feedback_data.prediction_id} not found"
        )
    
    # Create feedback
    feedback_dict = feedback_data.dict()
    feedback_dict["user_id"] = current_user.id
    
    feedback = crud.create_feedback(db, feedback_dict)
    
    return {
        "id": feedback.id,
        "prediction_id": feedback.prediction_id,
        "user_id": feedback.user_id,
        "feedback_type": feedback.feedback_type,
        "comments": feedback.comments,
        "created_at": feedback.created_at.isoformat() if feedback.created_at else None,
        "user_name": current_user.full_name
    }

@router.get("/prediction/{prediction_id}", response_model=List[FeedbackResponse])
async def get_feedback_for_prediction(
    prediction_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all feedback for a specific prediction
    """
    # Check if prediction exists
    prediction = crud.get_prediction(db, prediction_id)
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction {prediction_id} not found"
        )
    
    # Get feedback
    feedback_list = crud.get_feedback_for_prediction(db, prediction_id)
    
    # Format response
    result = []
    for feedback in feedback_list:
        # Get user name
        user = crud.get_user(db, feedback.user_id)
        user_name = user.full_name if user else None
        
        result.append({
            "id": feedback.id,
            "prediction_id": feedback.prediction_id,
            "user_id": feedback.user_id,
            "feedback_type": feedback.feedback_type,
            "comments": feedback.comments,
            "created_at": feedback.created_at.isoformat() if feedback.created_at else None,
            "user_name": user_name
        })
    
    return result

@router.get("/user/{user_id}", response_model=List[FeedbackResponse])
async def get_feedback_by_user(
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all feedback submitted by a specific user
    """
    # Check permissions - users can only access their own feedback unless admin
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's feedback"
        )
    
    # Check if user exists
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    # Get feedback
    feedback_list = crud.get_user_feedback(db, user_id, skip=skip, limit=limit)
    
    # Format response
    result = []
    for feedback in feedback_list:
        result.append({
            "id": feedback.id,
            "prediction_id": feedback.prediction_id,
            "user_id": feedback.user_id,
            "feedback_type": feedback.feedback_type,
            "comments": feedback.comments,
            "created_at": feedback.created_at.isoformat() if feedback.created_at else None,
            "user_name": user.full_name
        })
    
    return result

@router.get("/patient/{patient_id}", response_model=List[FeedbackResponse])
async def get_feedback_for_patient(
    patient_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all feedback related to predictions for a specific patient
    """
    # Check if patient exists
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    
    # Get predictions for patient
    predictions = crud.get_patient_predictions(db, patient_id)
    prediction_ids = [pred.id for pred in predictions]
    
    if not prediction_ids:
        return []
    
    # Get feedback for all predictions
    feedback_list = []
    for pred_id in prediction_ids:
        feedback_list.extend(crud.get_feedback_for_prediction(db, pred_id))
    
    # Apply pagination
    paginated_feedback = feedback_list[skip:skip+limit]
    
    # Format response
    result = []
    for feedback in paginated_feedback:
        # Get user name
        user = crud.get_user(db, feedback.user_id)
        user_name = user.full_name if user else None
        
        result.append({
            "id": feedback.id,
            "prediction_id": feedback.prediction_id,
            "user_id": feedback.user_id,
            "feedback_type": feedback.feedback_type,
            "comments": feedback.comments,
            "created_at": feedback.created_at.isoformat() if feedback.created_at else None,
            "user_name": user_name
        })
    
    return result
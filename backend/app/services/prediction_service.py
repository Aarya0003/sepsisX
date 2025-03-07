from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from loguru import logger
from datetime import datetime

from app.ml.inference import SepsisPredictor
from app.db import crud
from app.db.models import Patient, Alert, AlertStatus, SepsisPrediction, User
from app.services.notification import NotificationService

class PredictionService:
    def __init__(self):
        self.predictor = SepsisPredictor()
        self.notification_service = NotificationService()
    
    async def predict_sepsis_for_patient(
        self,
        db: Session,
        patient_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run sepsis prediction for a specific patient
        """
        try:
            # Get patient data
            patient = crud.get_patient(db, patient_id)
            if not patient:
                logger.error(f"Patient {patient_id} not found")
                return {"error": f"Patient {patient_id} not found"}
            
            # Get clinical data for the patient
            clinical_data = crud.get_patient_clinical_data(db, patient_id)
            if not clinical_data:
                logger.warning(f"No clinical data available for patient {patient_id}")
                return {"error": "No clinical data available for prediction"}
            
            # Convert SQLAlchemy models to dictionaries
            clinical_data_dicts = [
                {c.key: getattr(data, c.key) for c in data.__table__.columns}
                for data in clinical_data
            ]
            
            # Make prediction
            prediction_result = await self.predictor.predict_sepsis_risk(clinical_data_dicts)
            
            # Save prediction to database
            prediction_data = {
                "patient_id": patient_id,
                "user_id": user_id,
                "probability": prediction_result["probability"],
                "is_sepsis_risk": prediction_result["is_sepsis_risk"],
                "features_used": prediction_result["features_used"],
                "model_version": prediction_result["model_version"],
                "explanation": prediction_result["explanation"]
            }
            
            prediction = crud.create_sepsis_prediction(db, prediction_data)
            logger.info(f"Created sepsis prediction {prediction.id} for patient {patient_id}")
            
            # Generate alert if risk is detected
            if prediction_result["is_sepsis_risk"]:
                await self._create_alert_for_prediction(db, prediction, patient)
            
            # Prepare response
            patient_dict = {c.key: getattr(patient, c.key) for c in patient.__table__.columns}
            
            response = {
                "prediction_id": prediction.id,
                "patient": patient_dict,
                "prediction": prediction_result,
                "timestamp": datetime.now().isoformat()
            }
            
            return response
        
        except Exception as e:
            logger.error(f"Error in sepsis prediction: {str(e)}")
            return {"error": str(e)}
    
    async def _create_alert_for_prediction(
        self,
        db: Session,
        prediction: SepsisPrediction,
        patient: Patient
    ) -> Optional[Alert]:
        """
        Create an alert based on a sepsis prediction
        """
        try:
            # Generate alert details
            patient_dict = {c.key: getattr(patient, c.key) for c in patient.__table__.columns}
            alert_details = self.predictor.get_alert_details(
                {c.key: getattr(prediction, c.key) for c in prediction.__table__.columns},
                patient_dict
            )
            
            # Create alert in database
            alert_data = {
                "patient_id": patient.id,
                "prediction_id": prediction.id,
                "alert_type": alert_details["alert_type"],
                "severity": alert_details["severity"],
                "status": AlertStatus.PENDING,
                "message": alert_details["message"]
            }
            
            alert = crud.create_alert(db, alert_data)
            logger.info(f"Created alert {alert.id} for patient {patient.id}")
            
            # Notify users about the alert
            await self._notify_users_about_alert(db, alert, patient)
            
            return alert
        
        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}")
            return None
    
    async def _notify_users_about_alert(
        self,
        db: Session,
        alert: Alert,
        patient: Patient
    ) -> Dict[str, Any]:
        """
        Notify relevant users about a sepsis alert
        """
        try:
            # Get users to notify (here we're just getting all active doctors and nurses)
            # In a real system, you'd filter by department, assigned patients, etc.
            users = db.query(User).filter(
                User.is_active == True,
                (User.role == "doctor") | (User.role == "nurse")
            ).all()
            
            if not users:
                logger.warning("No users to notify about alert")
                return {"status": "no_users"}
            
            # Convert patient to dict for the notification service
            patient_dict = {c.key: getattr(patient, c.key) for c in patient.__table__.columns}
            
            # Send notifications
            notification_results = await self.notification_service.notify_users_of_alert(
                alert, patient_dict, users
            )
            
            logger.info(f"Notifications sent for alert {alert.id}: {notification_results}")
            return notification_results
        
        except Exception as e:
            logger.error(f"Error notifying users: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def batch_predict_sepsis(
        self,
        db: Session,
        patient_ids: List[str],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run sepsis prediction for multiple patients
        """
        results = {
            "successful": [],
            "failed": [],
            "total": len(patient_ids),
            "success_count": 0,
            "failure_count": 0
        }
        
        for patient_id in patient_ids:
            try:
                prediction_result = await self.predict_sepsis_for_patient(db, patient_id, user_id)
                if "error" not in prediction_result:
                    results["successful"].append({
                        "patient_id": patient_id,
                        "prediction_id": prediction_result["prediction_id"],
                        "is_sepsis_risk": prediction_result["prediction"]["is_sepsis_risk"],
                        "probability": prediction_result["prediction"]["probability"]
                    })
                    results["success_count"] += 1
                else:
                    results["failed"].append({
                        "patient_id": patient_id,
                        "error": prediction_result["error"]
                    })
                    results["failure_count"] += 1
            
            except Exception as e:
                logger.error(f"Error in batch prediction for patient {patient_id}: {str(e)}")
                results["failed"].append({
                    "patient_id": patient_id,
                    "error": str(e)
                })
                results["failure_count"] += 1
        
        return results
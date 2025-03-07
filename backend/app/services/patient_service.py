from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from loguru import logger
from datetime import datetime, timedelta

from app.db import crud
from app.fhir.client import FHIRClient
from app.fhir.parser import FHIRParser

class PatientService:
    def __init__(self):
        self.fhir_client = FHIRClient()
        self.fhir_parser = FHIRParser()
    
    async def sync_patient_from_fhir(
        self,
        db: Session,
        patient_id: str
    ) -> Dict[str, Any]:
        """
        Fetch patient data from FHIR and sync to local database
        """
        try:
            # Get patient from FHIR
            fhir_patient = self.fhir_client.get_patient(patient_id)
            
            # Parse FHIR patient to simplified structure
            parsed_patient = self.fhir_parser.parse_patient(fhir_patient)
            
            # Check if patient exists in our database
            db_patient = crud.get_patient(db, patient_id)
            
            if db_patient:
                # Update existing patient
                updated_patient = crud.update_patient(db, patient_id, parsed_patient)
                result = {
                    "status": "updated",
                    "patient_id": updated_patient.id,
                    "patient": {c.key: getattr(updated_patient, c.key) for c in updated_patient.__table__.columns}
                }
            else:
                # Create new patient
                new_patient = crud.create_patient(db, parsed_patient)
                result = {
                    "status": "created",
                    "patient_id": new_patient.id,
                    "patient": {c.key: getattr(new_patient, c.key) for c in new_patient.__table__.columns}
                }
            
            # Sync clinical data
            clinical_data_result = await self.sync_patient_clinical_data(db, patient_id)
            result["clinical_data"] = clinical_data_result
            
            return result
        
        except Exception as e:
            logger.error(f"Error syncing patient from FHIR: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def sync_patient_clinical_data(
        self,
        db: Session,
        patient_id: str
    ) -> Dict[str, Any]:
        """
        Fetch and sync clinical data for a patient from FHIR
        """
        try:
            # Get vital signs
            vital_signs = self.fhir_client.get_patient_observations(patient_id, "vital-signs")
            
            # Get lab results
            lab_results = self.fhir_client.get_patient_observations(patient_id, "laboratory")
            
            # Combine observations
            all_observations = vital_signs + lab_results
            
            # Parse and store each observation
            created_count = 0
            for entry in all_observations:
                if "resource" not in entry:
                    continue
                
                observation = entry["resource"]
                parsed_obs = self.fhir_parser.parse_observation(observation)
                
                # Check if we already have this observation
                existing_obs = db.query(crud.ClinicalData).filter(
                    crud.ClinicalData.fhir_resource_id == parsed_obs["fhir_resource_id"]
                ).first()
                
                if not existing_obs:
                    # Create new clinical data entry
                    crud.create_clinical_data(db, parsed_obs)
                    created_count += 1
            
            return {
                "status": "success", 
                "observations_processed": len(all_observations),
                "new_observations": created_count
            }
        
        except Exception as e:
            logger.error(f"Error syncing clinical data: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_patient_summary(
        self,
        db: Session,
        patient_id: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive patient summary including clinical data and predictions
        """
        try:
            # Get patient
            patient = crud.get_patient(db, patient_id)
            if not patient:
                return {"status": "error", "message": f"Patient {patient_id} not found"}
            
            # Get recent clinical data
            recent_clinical_data = crud.get_patient_clinical_data(db, patient_id, skip=0, limit=50)
            
            # Get latest vitals
            latest_vitals = self._extract_latest_vitals(recent_clinical_data)
            
            # Get recent sepsis predictions
            recent_predictions = crud.get_patient_predictions(db, patient_id, skip=0, limit=10)
            
            # Get active alerts
            active_alerts = db.query(crud.Alert).filter(
                crud.Alert.patient_id == patient_id,
                crud.Alert.status.in_(["pending", "acknowledged"])
            ).order_by(crud.Alert.created_at.desc()).all()
            
            # Format data for response
            return {
                "patient": {c.key: getattr(patient, c.key) for c in patient.__table__.columns if c.key != 'fhir_resource'},
                "latest_vitals": latest_vitals,
                "recent_clinical_data": [
                    {c.key: getattr(data, c.key) for c in data.__table__.columns if c.key != 'fhir_resource'} 
                    for data in recent_clinical_data[:10]  # Limit to most recent 10
                ],
                "sepsis_predictions": [
                    {c.key: getattr(pred, c.key) for c in pred.__table__.columns if c.key not in ['features_used', 'explanation']}
                    for pred in recent_predictions
                ],
                "latest_prediction": {c.key: getattr(recent_predictions[0], c.key) for c in recent_predictions[0].__table__.columns} if recent_predictions else None,
                "active_alerts": [
                    {c.key: getattr(alert, c.key) for c in alert.__table__.columns}
                    for alert in active_alerts
                ],
                "alert_count": len(active_alerts)
            }
        
        except Exception as e:
            logger.error(f"Error getting patient summary: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _extract_latest_vitals(self, clinical_data_list: List[Any]) -> Dict[str, Any]:
        """
        Extract the latest values for each vital sign from clinical data
        """
        vital_keys = [
            "heart_rate", "respiratory_rate", "temperature", 
            "systolic_bp", "diastolic_bp", "oxygen_saturation",
            "blood_glucose", "wbc_count", "platelet_count",
            "lactate", "creatinine", "bilirubin"
        ]
        
        latest_vitals = {}
        timestamps = {}
        
        for data in clinical_data_list:
            for key in vital_keys:
                value = getattr(data, key, None)
                if value is not None and (key not in latest_vitals or data.timestamp > timestamps.get(key, datetime.min)):
                    latest_vitals[key] = value
                    timestamps[key] = data.timestamp
        
        # Add timestamps to the output
        for key in latest_vitals.keys():
            latest_vitals[f"{key}_timestamp"] = timestamps[key].isoformat() if key in timestamps else None
        
        return latest_vitals
    
    async def search_patients(
        self,
        db: Session,
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search patients by name, MRN, etc.
        """
        try:
            # Search in local database first
            db_patients = db.query(crud.Patient).filter(
                (crud.Patient.first_name.ilike(f"%{query}%")) |
                (crud.Patient.last_name.ilike(f"%{query}%")) |
                (crud.Patient.mrn.ilike(f"%{query}%"))
            ).limit(limit).all()
            
            results = [
                {c.key: getattr(patient, c.key) for c in patient.__table__.columns if c.key != 'fhir_resource'}
                for patient in db_patients
            ]
            
            # If we have fewer than limit results, also search in FHIR
            if len(results) < limit:
                try:
                    # Search in FHIR
                    fhir_params = {
                        "name": query,
                        "_count": limit - len(results)
                    }
                    fhir_results = self.fhir_client.search_patients(fhir_params)
                    
                    # Process FHIR results
                    for entry in fhir_results:
                        if "resource" in entry:
                            # Parse patient and check if already in results
                            parsed_patient = self.fhir_parser.parse_patient(entry["resource"])
                            if not any(r["id"] == parsed_patient["id"] for r in results):
                                results.append(parsed_patient)
                
                except Exception as fhir_e:
                    logger.warning(f"FHIR search failed, using only local results: {str(fhir_e)}")
            
            return results
        
        except Exception as e:
            logger.error(f"Error searching patients: {str(e)}")
            return []
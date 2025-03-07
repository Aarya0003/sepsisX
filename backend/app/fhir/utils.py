from typing import Dict, List, Any, Optional
from datetime import datetime
import os
import json

def create_patient_resource(
    first_name: str,
    last_name: str,
    gender: Optional[str] = None,
    birth_date: Optional[str] = None,
    mrn: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    address: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a FHIR Patient resource
    """
    patient = {
        "resourceType": "Patient",
        "name": [
            {
                "use": "official",
                "family": last_name,
                "given": [first_name]
            }
        ],
        "telecom": []
    }
    
    if gender:
        patient["gender"] = gender.lower()
    
    if birth_date:
        patient["birthDate"] = birth_date
    
    if mrn:
        patient["identifier"] = [
            {
                "use": "official",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "MR",
                            "display": "Medical Record Number"
                        }
                    ],
                    "text": "Medical Record Number"
                },
                "value": mrn
            }
        ]
    
    if phone:
        patient["telecom"].append({
            "system": "phone",
            "value": phone,
            "use": "home"
        })
    
    if email:
        patient["telecom"].append({
            "system": "email",
            "value": email
        })
    
    if address:
        patient["address"] = [address]
    
    return patient

def create_observation_resource(
    patient_id: str,
    code: str,
    display: str,
    value: float,
    unit: str,
    date_time: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a FHIR Observation resource
    """
    if not date_time:
        date_time = datetime.now().isoformat()
    
    observation = {
        "resourceType": "Observation",
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "vital-signs",
                        "display": "Vital Signs"
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": code,
                    "display": display
                }
            ],
            "text": display
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "effectiveDateTime": date_time,
        "valueQuantity": {
            "value": value,
            "unit": unit,
            "system": "http://unitsofmeasure.org"
        }
    }
    
    return observation

def fhir_reference_to_id(reference: Optional[str]) -> Optional[str]:
    """
    Extract ID from a FHIR reference (e.g., "Patient/123" -> "123")
    """
    if not reference:
        return None
    
    parts = reference.split('/')
    if len(parts) >= 2:
        return parts[-1]
    
    return reference
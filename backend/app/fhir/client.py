import requests
from typing import Dict, List, Optional, Any, Union
import json
from requests.auth import HTTPBasicAuth
from loguru import logger
from datetime import datetime, timedelta

from app.core.config import settings

class FHIRClient:
    def __init__(
        self,
        base_url: str = settings.FHIR_API_URL,
        client_id: Optional[str] = settings.FHIR_CLIENT_ID,
        client_secret: Optional[str] = settings.FHIR_CLIENT_SECRET,
    ):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_token = None
        self.token_expiry = None
    
    def _get_auth_header(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        # If OAuth2 authentication is configured
        if self.client_id and self.client_secret:
            # Check if we need to refresh the token
            if not self.auth_token or not self.token_expiry or datetime.now() >= self.token_expiry:
                self._refresh_auth_token()
            
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        return headers
    
    def _refresh_auth_token(self) -> None:
        """
        Get OAuth2 token for FHIR API access
        """
        try:
            token_url = f"{self.base_url}/token"
            response = requests.post(
                token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            token_data = response.json()
            self.auth_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)  # Default to 1 hour
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
        except Exception as e:
            logger.error(f"Failed to get auth token: {str(e)}")
            raise e
    
    def get_patient(self, patient_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific patient by ID
        """
        url = f"{self.base_url}/Patient/{patient_id}"
        try:
            response = requests.get(url, headers=self._get_auth_header())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get patient {patient_id}: {str(e)}")
            raise e
    
    def search_patients(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for patients based on parameters
        """
        url = f"{self.base_url}/Patient"
        try:
            response = requests.get(url, params=params, headers=self._get_auth_header())
            response.raise_for_status()
            result = response.json()
            return result.get("entry", [])
        except Exception as e:
            logger.error(f"Failed to search patients: {str(e)}")
            raise e
    
    def get_patient_observations(self, patient_id: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all observations for a patient
        Optional category filter: vital-signs, laboratory, etc.
        """
        url = f"{self.base_url}/Observation"
        params = {
            "patient": patient_id,
            "_sort": "-date",
            "_count": 100,
        }
        
        if category:
            params["category"] = category
        
        try:
            response = requests.get(url, params=params, headers=self._get_auth_header())
            response.raise_for_status()
            result = response.json()
            return result.get("entry", [])
        except Exception as e:
            logger.error(f"Failed to get observations for patient {patient_id}: {str(e)}")
            raise e
    
    def get_patient_conditions(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Get all conditions (diagnoses) for a patient
        """
        url = f"{self.base_url}/Condition"
        params = {
            "patient": patient_id,
            "_sort": "-recorded-date",
            "_count": 100,
        }
        
        try:
            response = requests.get(url, params=params, headers=self._get_auth_header())
            response.raise_for_status()
            result = response.json()
            return result.get("entry", [])
        except Exception as e:
            logger.error(f"Failed to get conditions for patient {patient_id}: {str(e)}")
            raise e
    
    def get_patient_medications(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Get all medications for a patient
        """
        url = f"{self.base_url}/MedicationRequest"
        params = {
            "patient": patient_id,
            "_sort": "-authored",
            "_count": 100,
        }
        
        try:
            response = requests.get(url, params=params, headers=self._get_auth_header())
            response = requests.get(url, params=params, headers=self._get_auth_header())
            response.raise_for_status()
            result = response.json()
            return result.get("entry", [])
        except Exception as e:
            logger.error(f"Failed to get medications for patient {patient_id}: {str(e)}")
            raise e
    
    def get_patient_encounters(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Get all encounters for a patient
        """
        url = f"{self.base_url}/Encounter"
        params = {
            "patient": patient_id,
            "_sort": "-date",
            "_count": 100,
        }
        
        try:
            response = requests.get(url, params=params, headers=self._get_auth_header())
            response.raise_for_status()
            result = response.json()
            return result.get("entry", [])
        except Exception as e:
            logger.error(f"Failed to get encounters for patient {patient_id}: {str(e)}")
            raise e
    
    def create_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new patient record
        """
        url = f"{self.base_url}/Patient"
        try:
            response = requests.post(
                url,
                json=patient_data,
                headers=self._get_auth_header()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create patient: {str(e)}")
            raise e

    def create_observation(self, observation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new observation
        """
        url = f"{self.base_url}/Observation"
        try:
            response = requests.post(
                url,
                json=observation_data,
                headers=self._get_auth_header()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create observation: {str(e)}")
            raise e
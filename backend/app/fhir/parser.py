from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import re
from loguru import logger

class FHIRParser:
    @staticmethod
    def parse_patient(patient_resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse FHIR Patient resource into a simplified structure
        """
        try:
            patient_id = patient_resource.get("id")
            
            # Extract name
            name = patient_resource.get("name", [{}])[0]
            first_name = name.get("given", [""])[0] if name.get("given") else ""
            last_name = name.get("family", "")
            
            # Extract identifiers (like MRN)
            identifiers = patient_resource.get("identifier", [])
            mrn = None
            for identifier in identifiers:
                if identifier.get("type", {}).get("coding", [{}])[0].get("code") == "MR":
                    mrn = identifier.get("value")
                    break
            
            # Extract gender and DOB
            gender = patient_resource.get("gender")
            dob_str = patient_resource.get("birthDate")
            date_of_birth = None
            if dob_str:
                try:
                    date_of_birth = datetime.strptime(dob_str, "%Y-%m-%d")
                except ValueError:
                    logger.warning(f"Could not parse birthDate: {dob_str}")
            
            # Extract contact info
            telecom = patient_resource.get("telecom", [])
            phone_number = None
            email = None
            for contact in telecom:
                if contact.get("system") == "phone":
                    phone_number = contact.get("value")
                elif contact.get("system") == "email":
                    email = contact.get("value")
            
            # Extract address
            addresses = patient_resource.get("address", [])
            address = None
            if addresses:
                address_parts = []
                address_obj = addresses[0]
                
                line = address_obj.get("line", [])
                if line:
                    address_parts.extend(line)
                
                city = address_obj.get("city")
                if city:
                    address_parts.append(city)
                
                state = address_obj.get("state")
                if state:
                    address_parts.append(state)
                
                postal_code = address_obj.get("postalCode")
                if postal_code:
                    address_parts.append(postal_code)
                
                country = address_obj.get("country")
                if country:
                    address_parts.append(country)
                
                address = ", ".join(address_parts)
            
            return {
                "id": patient_id,
                "fhir_resource": patient_resource,
                "mrn": mrn,
                "first_name": first_name,
                "last_name": last_name,
                "date_of_birth": date_of_birth,
                "gender": gender,
                "phone_number": phone_number,
                "email": email,
                "address": address
            }
        except Exception as e:
            logger.error(f"Error parsing patient resource: {str(e)}")
            # Return a minimal valid patient object
            return {
                "id": patient_resource.get("id", "unknown"),
                "fhir_resource": patient_resource,
                "first_name": "Unknown",
                "last_name": "Patient"
            }
    
    @staticmethod
    def parse_observation(observation_resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse FHIR Observation resource into a simplified structure
        """
        try:
            # Extract basic details
            observation_id = observation_resource.get("id")
            patient_id = observation_resource.get("subject", {}).get("reference", "").replace("Patient/", "")
            
            # Extract timestamp
            effective_datetime = observation_resource.get("effectiveDateTime") or observation_resource.get("issued")
            timestamp = None
            if effective_datetime:
                try:
                    timestamp = datetime.fromisoformat(effective_datetime.replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    logger.warning(f"Could not parse datetime: {effective_datetime}")
                    timestamp = datetime.now()
            else:
                timestamp = datetime.now()
            
            # Extract code and display name
            code = observation_resource.get("code", {})
            coding = code.get("coding", [{}])[0]
            code_value = coding.get("code")
            code_display = coding.get("display")
            
            # Extract value
            value = None
            value_type = None
            
            if "valueQuantity" in observation_resource:
                value_quantity = observation_resource.get("valueQuantity", {})
                value = value_quantity.get("value")
                value_type = "quantity"
                unit = value_quantity.get("unit")
            elif "valueCodeableConcept" in observation_resource:
                value_codeable = observation_resource.get("valueCodeableConcept", {})
                value_coding = value_codeable.get("coding", [{}])[0]
                value = value_coding.get("display") or value_coding.get("code")
                value_type = "concept"
            elif "valueString" in observation_resource:
                value = observation_resource.get("valueString")
                value_type = "string"
            elif "valueBoolean" in observation_resource:
                value = observation_resource.get("valueBoolean")
                value_type = "boolean"
            elif "valueInteger" in observation_resource:
                value = observation_resource.get("valueInteger")
                value_type = "integer"
            elif "valueRange" in observation_resource:
                value_range = observation_resource.get("valueRange", {})
                low = value_range.get("low", {}).get("value")
                high = value_range.get("high", {}).get("value")
                value = f"{low}-{high}" if low and high else (low or high)
                value_type = "range"
            elif "valueRatio" in observation_resource:
                value_ratio = observation_resource.get("valueRatio", {})
                numerator = value_ratio.get("numerator", {}).get("value")
                denominator = value_ratio.get("denominator", {}).get("value")
                if numerator is not None and denominator is not None and denominator != 0:
                    value = numerator / denominator
                else:
                    value = None
                value_type = "ratio"
            
            # Map common vital signs and lab values to standardized fields
            clinical_data = {
                "patient_id": patient_id,
                "fhir_resource_id": observation_id,
                "fhir_resource_type": "Observation",
                "fhir_resource": observation_resource,
                "timestamp": timestamp
            }
            
            # Map specific vital signs and lab values based on LOINC or SNOMED codes
            if code_value:
                # Heart rate (LOINC: 8867-4)
                if code_value == "8867-4" or "heart rate" in (code_display or "").lower():
                    clinical_data["heart_rate"] = float(value) if value is not None else None
                
                # Respiratory rate (LOINC: 9279-1)
                elif code_value == "9279-1" or "respiratory rate" in (code_display or "").lower():
                    clinical_data["respiratory_rate"] = float(value) if value is not None else None
                
                # Body temperature (LOINC: 8310-5)
                elif code_value == "8310-5" or "temperature" in (code_display or "").lower():
                    clinical_data["temperature"] = float(value) if value is not None else None
                
                # Systolic blood pressure (LOINC: 8480-6)
                elif code_value == "8480-6" or "systolic" in (code_display or "").lower():
                    clinical_data["systolic_bp"] = float(value) if value is not None else None
                
                # Diastolic blood pressure (LOINC: 8462-4)
                elif code_value == "8462-4" or "diastolic" in (code_display or "").lower():
                    clinical_data["diastolic_bp"] = float(value) if value is not None else None
                
                # Oxygen saturation (LOINC: 2708-6)
                elif code_value == "2708-6" or "oxygen" in (code_display or "").lower():
                    clinical_data["oxygen_saturation"] = float(value) if value is not None else None
                
                # Blood glucose (LOINC: 2339-0)
                elif code_value == "2339-0" or "glucose" in (code_display or "").lower():
                    clinical_data["blood_glucose"] = float(value) if value is not None else None
                
                # WBC count (LOINC: 6690-2)
                elif code_value == "6690-2" or "white blood cell" in (code_display or "").lower() or "wbc" in (code_display or "").lower():
                    clinical_data["wbc_count"] = float(value) if value is not None else None
                
                # Platelet count (LOINC: 777-3)
                elif code_value == "777-3" or "platelet" in (code_display or "").lower():
                    clinical_data["platelet_count"] = float(value) if value is not None else None
                
                # Lactate (LOINC: 2524-7)
                elif code_value == "2524-7" or "lactate" in (code_display or "").lower():
                    clinical_data["lactate"] = float(value) if value is not None else None
                
                # Creatinine (LOINC: 2160-0)
                elif code_value == "2160-0" or "creatinine" in (code_display or "").lower():
                    clinical_data["creatinine"] = float(value) if value is not None else None
                
                # Bilirubin (LOINC: 1975-2)
                elif code_value == "1975-2" or "bilirubin" in (code_display or "").lower():
                    clinical_data["bilirubin"] = float(value) if value is not None else None
            
            return clinical_data
            
        except Exception as e:
            logger.error(f"Error parsing observation resource: {str(e)}")
            # Return minimal valid clinical data
            return {
                "patient_id": observation_resource.get("subject", {}).get("reference", "").replace("Patient/", ""),
                "fhir_resource_id": observation_resource.get("id", "unknown"),
                "fhir_resource_type": "Observation",
                "fhir_resource": observation_resource,
                "timestamp": datetime.now()
            }
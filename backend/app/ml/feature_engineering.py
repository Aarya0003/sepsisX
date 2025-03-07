from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger

def extract_features_from_clinical_data(
    clinical_data_list: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Extract features from a list of clinical data records
    Prioritizes the most recent values but also calculates trends
    """
    if not clinical_data_list:
        logger.warning("No clinical data provided for feature extraction")
        return {}
    
    # Sort clinical data by timestamp (most recent first)
    sorted_data = sorted(
        clinical_data_list, 
        key=lambda x: x.get("timestamp", datetime.min), 
        reverse=True
    )
    
    # Get the most recent record
    most_recent = sorted_data[0]
    
    # Initialize feature dictionary with the most recent values
    features = {
        "heart_rate": most_recent.get("heart_rate"),
        "respiratory_rate": most_recent.get("respiratory_rate"),
        "temperature": most_recent.get("temperature"),
        "systolic_bp": most_recent.get("systolic_bp"),
        "diastolic_bp": most_recent.get("diastolic_bp"),
        "oxygen_saturation": most_recent.get("oxygen_saturation"),
        "blood_glucose": most_recent.get("blood_glucose"),
        "wbc_count": most_recent.get("wbc_count"),
        "platelet_count": most_recent.get("platelet_count"),
        "lactate": most_recent.get("lactate"),
        "creatinine": most_recent.get("creatinine"),
        "bilirubin": most_recent.get("bilirubin")
    }
    
    # Calculate trends if we have more than one record
    if len(sorted_data) > 1:
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(sorted_data)
        
        # Ensure timestamp is datetime type
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # Sort by timestamp (oldest first for trend calculation)
        df = df.sort_values("timestamp")
        
        # Calculate trends for key vital signs using last 24 hours of data if available
        now = df["timestamp"].max()
        last_24h = now - timedelta(hours=24)
        recent_df = df[df["timestamp"] >= last_24h]
        
        # Only calculate trends if we have multiple readings in the last 24 hours
        if len(recent_df) > 1:
            try:
                # Heart rate trend
                if not recent_df["heart_rate"].isna().all():
                    hr_trend = calculate_trend(recent_df, "heart_rate")
                    features["heart_rate_trend"] = hr_trend
                
                # Respiratory rate trend
                if not recent_df["respiratory_rate"].isna().all():
                    rr_trend = calculate_trend(recent_df, "respiratory_rate")
                    features["respiratory_rate_trend"] = rr_trend
                
                # Temperature trend
                if not recent_df["temperature"].isna().all():
                    temp_trend = calculate_trend(recent_df, "temperature")
                    features["temperature_trend"] = temp_trend
                
                # Blood pressure trends
                if not recent_df["systolic_bp"].isna().all():
                    sys_trend = calculate_trend(recent_df, "systolic_bp")
                    features["systolic_bp_trend"] = sys_trend
                
                # Calculate WBC trend
                if not recent_df["wbc_count"].isna().all():
                    wbc_trend = calculate_trend(recent_df, "wbc_count")
                    features["wbc_count_trend"] = wbc_trend
                
                # Calculate lactate trend
                if not recent_df["lactate"].isna().all():
                    lactate_trend = calculate_trend(recent_df, "lactate")
                    features["lactate_trend"] = lactate_trend
            except Exception as e:
                logger.error(f"Error calculating trends: {str(e)}")
    
    # Add derived features
    try:
        # Calculate shock index if HR and systolic BP are available
        if features["heart_rate"] is not None and features["systolic_bp"] is not None and features["systolic_bp"] > 0:
            features["shock_index"] = features["heart_rate"] / features["systolic_bp"]
        
        # Calculate qSOFA score components
        # 1. Altered mental status - This would come from a different source, defaulting to 0
        # 2. Respiratory rate >= 22
        # 3. Systolic BP <= 100
        qsofa_score = 0
        if features["respiratory_rate"] is not None and features["respiratory_rate"] >= 22:
            qsofa_score += 1
        if features["systolic_bp"] is not None and features["systolic_bp"] <= 100:
            qsofa_score += 1
        features["qsofa_partial_score"] = qsofa_score
        
        # Calculate SIRS criteria components
        # 1. Temperature > 38°C or < 36°C
        # 2. Heart rate > 90
        # 3. Respiratory rate > 20
        # 4. WBC > 12,000 or < 4,000
        sirs_score = 0
        if features["temperature"] is not None and (features["temperature"] > 38.0 or features["temperature"] < 36.0):
            sirs_score += 1
        if features["heart_rate"] is not None and features["heart_rate"] > 90:
            sirs_score += 1
        if features["respiratory_rate"] is not None and features["respiratory_rate"] > 20:
            sirs_score += 1
        if features["wbc_count"] is not None and (features["wbc_count"] > 12.0 or features["wbc_count"] < 4.0):
            sirs_score += 1
        features["sirs_score"] = sirs_score
    
    except Exception as e:
        logger.error(f"Error calculating derived features: {str(e)}")
    
    # Remove None values
    features = {k: v for k, v in features.items() if v is not None}
    
    return features

def calculate_trend(df: pd.DataFrame, column: str) -> float:
    """
    Calculate the trend (slope) of a clinical parameter over time
    Returns positive value for increasing trend, negative for decreasing
    """
    # Drop NaN
    from typing import Dict, List, Any, Optional, Tuple
from loguru import logger
from datetime import datetime
import os

from app.ml.model import SepsisModel
from app.ml.feature_engineering import extract_features_from_clinical_data

class SepsisPredictor:
    def __init__(self):
        self.model = SepsisModel()
        logger.info("Initialized SepsisPredictor")
    
    async def predict_sepsis_risk(
        self, clinical_data_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process clinical data and predict sepsis risk
        """
        try:
            # Extract features from clinical data
            features = extract_features_from_clinical_data(clinical_data_list)
            logger.info(f"Extracted {len(features)} features for prediction")
            
            # Make prediction
            prediction_result = self.model.predict(features)
            logger.info(f"Prediction complete: risk={prediction_result['is_sepsis_risk']}, probability={prediction_result['probability']:.4f}")
            
            return prediction_result
        
        except Exception as e:
            logger.error(f"Error during sepsis prediction: {str(e)}")
            # Return safe default prediction
            return {
                "probability": 0.1,
                "is_sepsis_risk": False,
                "features_used": features if 'features' in locals() else {},
                "model_version": self.model.model_version,
                "explanation": None
            }
    
    def get_risk_factors(self, prediction_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract risk factors from prediction explanation
        """
        risk_factors = []
        try:
            # Check if we have explanation data
            if not prediction_result.get("explanation"):
                return risk_factors
            
            explanation = prediction_result["explanation"]
            features = explanation.get("features", [])
            shap_values = explanation.get("shap_values", [])
            
            # Sort features by absolute SHAP value (impact on prediction)
            feature_impacts = [(features[i], shap_values[i]) for i in range(len(features))]
            feature_impacts.sort(key=lambda x: abs(x[1]), reverse=True)
            
            # Get top risk factors (both positive and negative impact)
            for feature_name, shap_value in feature_impacts:
                # Get the actual feature value
                feature_value = prediction_result.get("features_used", {}).get(feature_name)
                if feature_value is None:
                    continue
                
                # Determine if this is a risk factor (positive SHAP value) or protective factor
                impact_type = "risk_factor" if shap_value > 0 else "protective_factor"
                
                # Calculate relative contribution percentage
                total_impact = sum(abs(val) for val in shap_values)
                contribution_pct = (abs(shap_value) / total_impact * 100) if total_impact > 0 else 0
                
                risk_factors.append({
                    "feature_name": feature_name,
                    "value": feature_value,
                    "impact": shap_value,
                    "impact_type": impact_type,
                    "contribution_pct": contribution_pct
                })
            
            return risk_factors
        
        except Exception as e:
            logger.error(f"Error extracting risk factors: {str(e)}")
            return []
    
    def get_alert_details(
        self, 
        prediction_result: Dict[str, Any], 
        patient_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate alert details based on prediction result
        """
        try:
            probability = prediction_result.get("probability", 0)
            is_sepsis_risk = prediction_result.get("is_sepsis_risk", False)
            
            # Determine severity level based on probability
            if probability >= 0.8:
                severity = 5  # Critical
                alert_type = "CRITICAL_SEPSIS_RISK"
            elif probability >= 0.6:
                severity = 4  # High
                alert_type = "HIGH_SEPSIS_RISK"
            elif probability >= 0.5:
                severity = 3  # Medium
                alert_type = "MEDIUM_SEPSIS_RISK"
            elif probability >= 0.3:
                severity = 2  # Low
                alert_type = "LOW_SEPSIS_RISK"
            else:
                severity = 1  # Minimal
                alert_type = "MINIMAL_RISK"
            
            # Generate alert message
            patient_name = ""
            if patient_data:
                patient_name = f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}".strip()
            
            if is_sepsis_risk:
                if patient_name:
                    message = f"SEPSIS ALERT: Patient {patient_name} has a {probability:.1%} probability of developing sepsis. Immediate assessment recommended."
                else:
                    message = f"SEPSIS ALERT: Patient has a {probability:.1%} probability of developing sepsis. Immediate assessment recommended."
            else:
                if patient_name:
                    message = f"Patient {patient_name} has a {probability:.1%} probability of developing sepsis. Regular monitoring advised."
                else:
                    message = f"Patient has a {probability:.1%} probability of developing sepsis. Regular monitoring advised."
            
            # Get risk factors
            risk_factors = self.get_risk_factors(prediction_result)
            
            return {
                "alert_type": alert_type,
                "severity": severity,
                "message": message,
                "is_sepsis_risk": is_sepsis_risk,
                "probability": probability,
                "risk_factors": risk_factors
            }
        
        except Exception as e:
            logger.error(f"Error generating alert details: {str(e)}")
            return {
                "alert_type": "SYSTEM_ERROR",
                "severity": 3,
                "message": "Error generating sepsis risk assessment. Please check the patient data manually.",
                "is_sepsis_risk": False,
                "probability": 0.0,
                "risk_factors": []
            }
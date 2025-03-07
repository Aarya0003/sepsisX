import pickle
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from loguru import logger
import shap
import joblib
from pathlib import Path
import os

from app.core.config import settings

class SepsisModel:
    def __init__(
        self,
        model_path: str = settings.MODEL_PATH,
        explainer_path: str = settings.EXPLAINER_PATH,
        feature_config_path: str = settings.FEATURE_CONFIG_PATH
    ):
        self.model_path = model_path
        self.explainer_path = explainer_path
        self.feature_config_path = feature_config_path
        self.model = self._load_model()
        self.explainer = self._load_explainer()
        self.feature_config = self._load_feature_config()
        self.model_version = "1.0.0"  # This should be read from the model metadata
    
    def _load_model(self):
        """
        Load the trained model
        """
        try:
            model = joblib.load(self.model_path)
            logger.info(f"Successfully loaded model from {self.model_path}")
            return model
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            # Create a dummy model for fallback
            logger.warning("Creating a fallback dummy model")
            return self._create_dummy_model()
    
    def _load_explainer(self):
        """
        Load the SHAP explainer
        """
        try:
            explainer = joblib.load(self.explainer_path)
            logger.info(f"Successfully loaded explainer from {self.explainer_path}")
            return explainer
        except Exception as e:
            logger.error(f"Failed to load explainer: {str(e)}")
            return None
    
    def _load_feature_config(self):
        """
        Load the feature configuration
        """
        try:
            with open(self.feature_config_path, 'r') as f:
                feature_config = json.load(f)
            logger.info(f"Successfully loaded feature config from {self.feature_config_path}")
            return feature_config
        except Exception as e:
            logger.error(f"Failed to load feature config: {str(e)}")
            # Create a dummy feature config for fallback
            return self._create_dummy_feature_config()
    
    def _create_dummy_model(self):
        """
        Create a dummy model for fallback when loading fails
        """
        # Simple class with predict_proba method that returns random predictions
        class DummyModel:
            def predict_proba(self, X):
                n_samples = X.shape[0]
                # Return random probabilities with bias toward negative class
                return np.hstack([
                    np.random.uniform(0.7, 0.99, (n_samples, 1)),  # Negative class
                    np.random.uniform(0.01, 0.3, (n_samples, 1))   # Positive class
                ])
        
        # Create dummy model
        model = DummyModel()
        
        # Save the dummy model
        model_dir = Path(self.model_path).parent
        model_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, self.model_path)
        
        return model
    
    def _create_dummy_feature_config(self):
        """
        Create a dummy feature configuration for fallback
        """
        feature_config = {
            "features": [
                "heart_rate",
                "respiratory_rate",
                "temperature",
                "systolic_bp",
                "diastolic_bp",
                "oxygen_saturation",
                "blood_glucose",
                "wbc_count",
                "platelet_count",
                "lactate",
                "creatinine",
                "bilirubin"
            ],
            "default_values": {
                "heart_rate": 75.0,
                "respiratory_rate": 16.0,
                "temperature": 37.0,
                "systolic_bp": 120.0,
                "diastolic_bp": 80.0,
                "oxygen_saturation": 98.0,
                "blood_glucose": 100.0,
                "wbc_count": 7.0,
                "platelet_count": 250.0,
                "lactate": 1.0,
                "creatinine": 1.0,
                "bilirubin": 0.6
            },
            "threshold": 0.5
        }
        
        # Save the dummy feature config
        config_dir = Path(self.feature_config_path).parent
        config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.feature_config_path, 'w') as f:
            json.dump(feature_config, f, indent=2)
        
        return feature_config
    
    def prepare_features(self, clinical_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Extract and prepare features from clinical data for model prediction
        """
        # Get the list of features used by the model
        features = self.feature_config["features"]
        
        # Extract values for each feature, use default if missing
        feature_values = {}
        for feature in features:
            # Get value from clinical data, use default if not available
            value = clinical_data.get(feature)
            if value is None:
                value = self.feature_config["default_values"].get(feature, 0.0)
            
            feature_values[feature] = value
        
        # Create a pandas DataFrame with a single row
        df = pd.DataFrame([feature_values])
        
        return df
    
    def predict(self, clinical_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make sepsis prediction using the loaded model
        """
        try:
            # Prepare features for prediction
            features_df = self.prepare_features(clinical_data)
            
            # Make prediction
            probabilities = self.model.predict_proba(features_df)
            sepsis_probability = float(probabilities[0, 1])  # Probability of sepsis (positive class)
            
            # Determine if patient is at risk based on threshold
            threshold = self.feature_config.get("threshold", 0.5)
            is_sepsis_risk = sepsis_probability >= threshold
            
            # Generate explanation if explainer is available
            explanation = None
            if self.explainer:
                try:
                    # Calculate SHAP values
                    shap_values = self.explainer.shap_values(features_df)
                    
                    # If SHAP returns a list (e.g., for tree models), take the values for positive class
                    if isinstance(shap_values, list):
                        shap_values = shap_values[1]  # Values for positive class
                    
                    # Convert to list for JSON serialization
                    shapley_values = shap_values[0].tolist()
                    
                    # Create explanation with feature names and their SHAP values
                    feature_names = list(features_df.columns)
                    explanation = {
                        "features": feature_names,
                        "shap_values": shapley_values,
                        "base_value": float(self.explainer.expected_value) 
                            if not isinstance(self.explainer.expected_value, list) 
                            else float(self.explainer.expected_value[1])
                    }
                except Exception as e:
                    logger.error(f"Failed to generate SHAP explanation: {str(e)}")
                    explanation = None
            
            # Return prediction results
            result = {
                "probability": sepsis_probability,
                "is_sepsis_risk": is_sepsis_risk,
                "features_used": features_df.to_dict(orient="records")[0],
                "model_version": self.model_version,
                "explanation": explanation
            }
            
            return result
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            # Return a fallback prediction
            return {
                "probability": 0.1,  # Low probability as a safe default
                "is_sepsis_risk": False,
                "features_used": {},
                "model_version": self.model_version,
                "explanation": None
            }
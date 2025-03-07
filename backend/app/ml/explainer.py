from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from loguru import logger
import joblib
import shap

class SepsisExplainer:
    def __init__(self, model, feature_names: List[str]):
        """
        Initialize the explainer with a trained model and feature names
        """
        self.model = model
        self.feature_names = feature_names
        self.explainer = self._create_explainer()
    
    def _create_explainer(self):
        """
        Create a SHAP explainer for the model
        """
        try:
            # Create a background dataset for the explainer
            # Use zeros as a simple default
            background_data = pd.DataFrame(np.zeros((1, len(self.feature_names))), columns=self.feature_names)
            
            # Determine the type of model and create appropriate explainer
            model_type = str(type(self.model).__name__).lower()
            
            if "xgb" in model_type:
                # XGBoost model
                return shap.TreeExplainer(self.model)
            elif "lightgbm" in model_type:
                # LightGBM model
                return shap.TreeExplainer(self.model)
            elif "random" in model_type and "forest" in model_type:
                # Random Forest model
                return shap.TreeExplainer(self.model)
            elif "linear" in model_type or "logistic" in model_type:
                # Linear/Logistic model
                return shap.LinearExplainer(self.model, background_data)
            else:
                # Default to Kernel explainer for other models
                # This is slower but works with any model
                return shap.KernelExplainer(
                    lambda x: self.model.predict_proba(x)[:, 1], 
                    background_data
                )
        
        except Exception as e:
            logger.error(f"Failed to create explainer: {str(e)}")
            return None
    
    def explain_prediction(self, features_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate explanation for a prediction
        """
        if self.explainer is None:
            logger.warning("No explainer available")
            return {}
        
        try:
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(features_df)
            
            # Handle different return types from different explainers
            if isinstance(shap_values, list):
                # For tree-based models, it returns a list with values for each class
                values = shap_values[1] if len(shap_values) > 1 else shap_values[0]
            else:
                values = shap_values
            
            # Get expected value (base value)
            if hasattr(self.explainer, 'expected_value'):
                if isinstance(self.explainer.expected_value, list):
                    base_value = self.explainer.expected_value[1]
                else:
                    base_value = self.explainer.expected_value
            else:
                base_value = 0.5  # Default for binary classification
            
            # Create explanation
            explanation = {
                "features": self.feature_names,
                "shap_values": values[0].tolist(),
                "base_value": float(base_value)
            }
            
            return explanation
        
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            return {}
    
    def generate_force_plot_image(self, features_df: pd.DataFrame) -> Optional[str]:
        """
        Generate a SHAP force plot as a base64 encoded image
        """
        if self.explainer is None:
            logger.warning("No explainer available")
            return None
        
        try:
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(features_df)
            
            # For tree-based models, it returns a list with values for each class
            if isinstance(shap_values, list) and len(shap_values) > 1:
                values = shap_values[1]  # Values for positive class
                expected_value = self.explainer.expected_value[1]
            else:
                values = shap_values
                expected_value = self.explainer.expected_value
            
            # Create force plot
            plt.figure(figsize=(10, 3))
            force_plot = shap.force_plot(
                expected_value, 
                values[0], 
                features_df.iloc[0], 
                matplotlib=True,
                show=False
            )
            
            # Convert plot to image
            plt.tight_layout()
            img_buf = io.BytesIO()
            plt.savefig(img_buf, format='png', dpi=150, bbox_inches='tight')
            plt.close()
            
            # Encode image to base64
            img_buf.seek(0)
            img_data = base64.b64encode(img_buf.read()).decode('utf-8')
            
            return f"data:image/png;base64,{img_data}"
        
        except Exception as e:
            logger.error(f"Error generating force plot: {str(e)}")
            return None
    
    def generate_waterfall_plot_image(self, features_df: pd.DataFrame) -> Optional[str]:
        """
        Generate a SHAP waterfall plot as a base64 encoded image
        """
        if self.explainer is None:
            logger.warning("No explainer available")
            return None
        
        try:
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(features_df)
            
            # Handle different return types from different explainers
            if isinstance(shap_values, list) and len(shap_values) > 1:
                values = shap_values[1]  # Values for positive class
            else:
                values = shap_values
            
            # Create waterfall plot
            plt.figure(figsize=(10, 6))
            shap.plots._waterfall.waterfall_legacy(
                self.explainer.expected_value[1] if isinstance(self.explainer.expected_value, list) else self.explainer.expected_value,
                values[0],
                features_df.iloc[0],
                show=False
            )
            
            # Convert plot to image
            plt.tight_layout()
            img_buf = io.BytesIO()
            plt.savefig(img_buf, format='png', dpi=150, bbox_inches='tight')
            plt.close()
            
            # Encode image to base64
            img_buf.seek(0)
            img_data = base64.b64encode(img_buf.read()).decode('utf-8')
            
            return f"data:image/png;base64,{img_data}"
        
        except Exception as e:
            logger.error(f"Error generating waterfall plot: {str(e)}")
            return None
    
    def save_explainer(self, path: str) -> bool:
        """
        Save the explainer to disk
        """
        try:
            joblib.dump(self.explainer, path)
            logger.info(f"Explainer saved to {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save explainer: {str(e)}")
            return False
"""
Explainability module using SHAP.
"""

import shap
import pandas as pd
from typing import Dict, Any

def explain_prediction(model_instance, features: pd.DataFrame) -> Dict[str, Any]:
    """
    Returns top SHAP features and their specific impact.
    Uses shap.TreeExplainer explicitly designed for LightGBM models.
    """
    # Assuming model_instance is our CreditScoringModel class 
    # Extract the underlying lightgbm.Booster object
    booster = model_instance.model
    
    # Init tree explainer
    explainer = shap.TreeExplainer(booster)
    
    # Calculate SHAP values
    shap_values = explainer.shap_values(features)
    
    # For LightGBM regression/binary classification, shap_values is typically a 2D array [samples x features]
    # For multiclass, it may be a list. We extract the array for our 1 prediction sample
    if isinstance(shap_values, list):
         # Get values from the positive class
         val_arr = shap_values[1][0] 
    else:
         val_arr = shap_values[0]
         
    feature_names = features.columns.tolist()
    feature_values = features.iloc[0].values
    
    # Build list of feature dictionaries
    impacts = []
    for i, val in enumerate(val_arr):
        impacts.append({
            "feature": feature_names[i],
            "value": round(float(feature_values[i]), 2),
            "impact": round(float(val), 4)
        })
        
    # Sort absolute magnitude to find top impactors (both positive / negative)
    impacts.sort(key=lambda x: abs(x["impact"]), reverse=True)
    
    # We want top 5 features
    top_features = impacts[:5]
    
    # We can get prediction decision easily
    prediction_info = model_instance.predict(features)
    
    return {
        "predicted_score": prediction_info["predicted_score"],
        "decision": prediction_info["decision"],
        "top_features": top_features
    }

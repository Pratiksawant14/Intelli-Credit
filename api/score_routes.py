"""
FastAPI routes for model scoring and SHAP explanations.
"""
from fastapi import APIRouter
from typing import Dict, Any

from nlp_module.ner_extractor import extract_entities
from ml_engine.features import extract_features
from ml_engine.model import CreditScoringModel
from ml_engine.explain import explain_prediction

router = APIRouter()

# Load model globally for the app
scoring_model = CreditScoringModel()
scoring_model.load_model("model_artifacts/lgbm_mock_model.pkl")

@router.post("/score/")
async def score_company(parsed_data: Dict[str, Any]):
    """
    Accepts raw text or document data, extracts NLP entities, engineers features,
    and returns a credit score with SHAP explainability.
    """
    document_data = parsed_data.get("document_data", {})
    raw_text = parsed_data.get("raw_text", "")
    
    # 1. Extract NLP Entities
    entities = extract_entities(raw_text)
    
    # 2. Feature Engineering
    features_df = extract_features(document_data, entities)
    
    # 3. Score
    prediction = scoring_model.predict(features_df)
    
    # 4. Explain
    explanation = explain_prediction(scoring_model, features_df)
    
    return {
        "status": "success",
        "nlp_entities": entities,
        "score_result": prediction,
        "explanation": explanation
    }

# test_ml.py
import json
from ml_engine.features import extract_features
from ml_engine.model import CreditScoringModel
from ml_engine.explain import explain_prediction

def run_test():
    # Mock data mirroring OCR extraction output
    document_data = {
        "extracted_revenue": 1000000,
        "extracted_expenses": 800000,   # ratio = 1.25
        "current_assets": 500000,
        "current_liabilities": 300000,  # WC = +200000
        "total_debt": 200000,
        "total_equity": 400000,         # ratio = 0.5
        "gst_turnover": 1000000,
        "bank_credits": 950000,         # ~0.95 score
        "sector_risk": 0
    }

    # Mock entity extraction (with one NPA mention)
    entity_data = [
        {"type": "ORG", "text": "Orbit Holdings Ltd."},
        {"type": "PERSON", "text": "Rakesh Mehta"},
        {"type": "LAW", "text": "Insolvency Act filing detected"},
        {"type": "ORG", "text": "Something about NPA"}
    ]

    print("1. Extracting Features...")
    features = extract_features(document_data, entity_data)
    print("Features Extracted:\n", features)

    print("\n2. Initializing & Loading Model...")
    model = CreditScoringModel(reject_threshold=0.6, watchlist_threshold=0.3)
    model.load_model("model_artifacts/lgbm_mock_model.pkl")
    
    print("\n3. Predicting...")
    prediction = model.predict(features)
    print("Prediction Result:\n", json.dumps(prediction, indent=2))

    print("\n4. Explaining Prediction with SHAP...")
    explanation = explain_prediction(model, features)
    print("Explanation:\n", json.dumps(explanation, indent=2))

if __name__ == "__main__":
    run_test()

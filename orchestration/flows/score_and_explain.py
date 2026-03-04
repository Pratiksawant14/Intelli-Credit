"""
Prefect flow: ML scoring -> SHAP explanations
"""
from prefect import flow, task
import pandas as pd

from ml_engine.model import CreditScoringModel
from ml_engine.explain import explain_prediction

@task
def load_and_score(features_df: pd.DataFrame):
    print("Scoring company...")
    model = CreditScoringModel()
    model.load_model("model_artifacts/lgbm_mock_model.pkl")
    prediction = model.predict(features_df)
    return model, prediction

@task
def run_shap(model, features_df: pd.DataFrame):
    print("Generating SHAP Explanations...")
    return explain_prediction(model, features_df)

@flow
def score_and_explain_flow(features_df: pd.DataFrame):
    model, prediction = load_and_score(features_df)
    explanation = run_shap(model, features_df)
    return {
        "prediction": prediction,
        "explanation": explanation
    }

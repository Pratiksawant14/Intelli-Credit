"""
Feature extraction for ML models.
Includes logic for GST-bank reconciliation, financial ratios, etc.
"""

import pandas as pd
from typing import Dict, List

def extract_features(document_data: Dict, entity_data: List[Dict]) -> pd.DataFrame:
    """
    Ingests cleaned outputs from the OCR pipeline (tables, text blocks) and NLP data.
    Computes basic financial ratios and other features.
    
    Returns a pandas DataFrame with a single feature row for scoring.
    """
    feature_dict = {
        "revenue_expense_ratio": 1.0,
        "working_capital": 0.0,
        "debt_equity_ratio": 0.0,
        "gst_bank_match_score": 0.0,
        "legal_flag_count": 0,
        "sector_risk_flag": 0
    }
    
    # Calculate Ratios based on typical extracted financials
    revenue = document_data.get("extracted_revenue", 1000000)
    expenses = document_data.get("extracted_expenses", 800000)
    
    if expenses > 0:
        feature_dict["revenue_expense_ratio"] = revenue / expenses
        
    current_assets = document_data.get("current_assets", 500000)
    current_liabilities = document_data.get("current_liabilities", 300000)
    feature_dict["working_capital"] = current_assets - current_liabilities
    
    debt = document_data.get("total_debt", 200000)
    equity = document_data.get("total_equity", 400000)
    if equity > 0:
        feature_dict["debt_equity_ratio"] = debt / equity
        
    # GST vs Bank match score (1.0 = perfect match, 0.0 = terrible match)
    gst_turnover = document_data.get("gst_turnover", 1000000)
    bank_credits = document_data.get("bank_credits", 950000)
    
    if max(gst_turnover, bank_credits) > 0:
        diff_pct = abs(gst_turnover - bank_credits) / max(gst_turnover, bank_credits)
        feature_dict["gst_bank_match_score"] = max(0.0, 1.0 - diff_pct)

    # Number of red flags from entities (e.g., LAW type entities, NPA mentions)
    red_flag_count = 0
    for ent in entity_data:
        if ent.get("type") in ["LAW"]:
            red_flag_count += 1
        # Check if the extracted entity text implies a problem
        text = ent.get("text", "").lower()
        if "npa" in text or "insolvency" in text or "default" in text:
            red_flag_count += 1
            
    feature_dict["legal_flag_count"] = red_flag_count
    
    # Sector risk flag (Example: 1 for high risk, 0 for normal)
    feature_dict["sector_risk_flag"] = document_data.get("sector_risk", 0)
    
    return pd.DataFrame([feature_dict])

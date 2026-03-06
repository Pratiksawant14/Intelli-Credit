def compute_loan_limit(risk_score: int, revenue: float, debt: float, ebitda: float, collateral_value: float, gst_reconciliation_score: float) -> dict:
    steps = []
    
    # Base limit: 20% of revenue
    base_limit = revenue * 0.20
    steps.append({"step": "Base Limit", "value": round(base_limit, 2), "reason": f"20% of annual revenue ({revenue})"})
    
    # EBITDA cap
    ebitda_cap = ebitda * 3.5
    steps.append({"step": "EBITDA Cap", "value": round(ebitda_cap, 2), "reason": f"3.5x EBITDA ({ebitda})"})
    
    current_limit = min(base_limit, ebitda_cap)
    steps.append({"step": "Minimum Bound", "value": round(current_limit, 2), "reason": "Lesser of Base Limit and EBITDA Cap"})
    
    # Risk Multipliers
    if risk_score >= 85:
        multiplier = 1.0
    elif 70 <= risk_score <= 84:
        multiplier = 0.85
    elif 60 <= risk_score <= 69:
        multiplier = 0.70
    elif 50 <= risk_score <= 59:
        multiplier = 0.50
    else:
        multiplier = 0.0
        
    current_limit *= multiplier
    steps.append({"step": "Risk Multiplier", "value": round(current_limit, 2), "reason": f"Multiplier {multiplier} applied for score {risk_score}"})
    
    if current_limit > 0:
        # Collateral Modifier
        if collateral_value == 0:
            current_limit *= 0.80
            steps.append({"step": "Collateral Penalty", "value": round(current_limit, 2), "reason": "No collateral provided (-20%)"})
        else:
            coverage = collateral_value / current_limit
            if coverage >= 1.25:
                steps.append({"step": "Collateral Modifier", "value": round(current_limit, 2), "reason": f"Strong coverage {round(coverage, 2)}x (No penalty)"})
            elif coverage < 1.0:
                current_limit *= 0.85
                steps.append({"step": "Collateral Penalty", "value": round(current_limit, 2), "reason": f"Weak coverage {round(coverage, 2)}x (-15%)"})
            else:
                steps.append({"step": "Collateral Modifier", "value": round(current_limit, 2), "reason": f"Adequate coverage {round(coverage, 2)}x (No penalty)"})
        
        # GST Penalty
        if gst_reconciliation_score < 60:
            current_limit *= 0.90
            steps.append({"step": "GST Penalty", "value": round(current_limit, 2), "reason": f"Low GST score {gst_reconciliation_score} (-10%)"})
    else:
        current_limit = 0.0
        steps.append({"step": "Final Adjustment", "value": 0.0, "reason": "Score is below acceptable limit."})

    return {
        "recommended_limit_cr": round(current_limit, 3),
        "limit_calculation_steps": steps
    }

def compute_interest_rate(risk_score: int, qualitative_delta: dict) -> dict:
    steps = []
    base_mclr = 9.5
    steps.append({"step": "Base MCLR", "value": base_mclr, "reason": "Internal Bank Benchmark Rate"})
    
    rate = base_mclr
    
    # Score premiums
    if risk_score >= 85:
        premium = 0.5
    elif 70 <= risk_score <= 84:
        premium = 1.25
    elif 60 <= risk_score <= 69:
        premium = 2.0
    elif 50 <= risk_score <= 59:
        premium = 3.0
    else:
        premium = 4.0 # Flat reject rate handling visually
        
    rate += premium
    steps.append({"step": "Risk Premium", "value": rate, "reason": f"+{premium}% for score {risk_score}"})
    
    # Qualitative loaded
    if qualitative_delta.get("pending_litigation") is True:
        rate += 0.5
        steps.append({"step": "Litigation Premium", "value": rate, "reason": "+0.5% for active litigation"})
        
    mgt = qualitative_delta.get("management_quality")
    if mgt == "WEAK":
        rate += 0.75
        steps.append({"step": "Management Premium", "value": rate, "reason": "+0.75% for weak management"})
        
    ind = qualitative_delta.get("industry_outlook")
    if ind == "ADVERSE":
        rate += 0.5
        steps.append({"step": "Industry Premium", "value": rate, "reason": "+0.5% for adverse industry"})
        
    col = qualitative_delta.get("collateral_quality")
    if col == "PRIME":
        rate -= 0.25
        steps.append({"step": "Collateral Discount", "value": rate, "reason": "-0.25% for prime collateral"})
        
    # Edge capping min 9.5, max 16.0
    final_rate = max(9.5, min(16.0, rate))
    if final_rate != rate:
        steps.append({"step": "Rate Cap Applied", "value": final_rate, "reason": f"Bounded to [9.5%, 16.0%] limit."})
        
    return {
        "recommended_rate_pct": round(final_rate, 2),
        "rate_calculation_steps": steps
    }

def generate_sanction_terms(limit: float, rate: float, risk_score: int) -> dict:
    if risk_score >= 70:
        decision = "APPROVE"
    elif 60 <= risk_score <= 69:
        decision = "CONDITIONAL_APPROVE"
    elif 50 <= risk_score <= 59:
        decision = "WATCHLIST"
    else:
        decision = "REJECT"
        
    tenure_months = 12
    facility_type = "Working Capital Facility"
    
    conditions_precedent = [
        "Execution of Master Facility Agreement.",
        "Submission of latest Audited Financials.",
        f"Creation of charge on current assets matching {limit} Cr."
    ]
    
    covenants = [
        "Maintain current asset coverage ratio above 1.1x at all times.",
        "Monthly submission of stock and book debt statements."
    ]
    
    if decision == "CONDITIONAL_APPROVE":
        conditions_precedent.append("Promoter personal guarantee is mandatory.")
    
    if decision == "WATCHLIST":
        covenants.append("Quarterly review of account with special mention tracking.")
        
    if limit == 0 or decision == "REJECT":
        conditions_precedent = []
        covenants = []
        facility_type = "None"
        tenure_months = 0
    
    return {
        "decision": decision,
        "facility_type": facility_type,
        "tenure_months": tenure_months,
        "conditions_precedent": conditions_precedent,
        "covenants": covenants
    }

if __name__ == "__main__":
    import json
    
    # Inline Verification Test
    risk_score = 72
    revenue = 42.5
    debt = 8.2
    ebitda = 6.1
    collateral_value = 12.0
    gst_reconciliation_score = 65
    qualitative_delta = {
        "pending_litigation": True, 
        "management_quality": "AVERAGE",
        "industry_outlook": "STABLE",
        "collateral_quality": "STANDARD"
    }

    limit_info = compute_loan_limit(risk_score, revenue, debt, ebitda, collateral_value, gst_reconciliation_score)
    rate_info = compute_interest_rate(risk_score, qualitative_delta)
    terms = generate_sanction_terms(limit_info["recommended_limit_cr"], rate_info["recommended_rate_pct"], risk_score)
    
    output = {
        "limit_info": limit_info,
        "rate_info": rate_info,
        "terms": terms
    }
    
    print(json.dumps(output, indent=2))

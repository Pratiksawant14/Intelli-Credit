import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Fallback to simple rules if spacy model isn't installed during the test
    nlp = lambda x: type('Doc', (object,), {'text': x})()

NEGATIVE_KEYWORDS = ["idle", "shutdown", "dispute", "delay", "loss", "vacant", "defaulted", "seized", "overdue", "stressed"]
POSITIVE_KEYWORDS = ["expansion", "export", "order book", "profit", "growth", "iso", "certified", "new contract", "capacity addition"]

def classify_free_text(text: str) -> dict:
    """
    Analyzes analyst free text to determine sentiment, extracted keywords, and risk category.
    """
    if not text:
        return {
            "risk_category": "LOW_RISK",
            "keywords_found": [],
            "sentiment_score": 0.0,
            "delta": 0
        }
        
    text_lower = text.lower()
    
    found_neg = [kw for kw in NEGATIVE_KEYWORDS if kw in text_lower]
    found_pos = [kw for kw in POSITIVE_KEYWORDS if kw in text_lower]
    
    pos_count = len(found_pos)
    neg_count = len(found_neg)
    
    sentiment_score = (pos_count - neg_count) / max(pos_count + neg_count, 1)
    
    # Calculate score delta
    raw_delta = (pos_count * 2) - (neg_count * 3)
    # Cap between -10 and +8
    delta = max(-10, min(8, raw_delta))
    
    # Determine risk category
    risk_category = "LOW_RISK"
    if any(kw in found_neg for kw in ["idle", "shutdown", "vacant", "seized"]):
        risk_category = "OPERATIONAL_RISK"
    elif any(kw in found_neg for kw in ["dispute", "defaulted", "overdue"]):
        risk_category = "MANAGEMENT_RISK"
    elif any(kw in found_neg for kw in ["delay", "stressed", "loss"]):
        risk_category = "MARKET_RISK"
        
    return {
        "risk_category": risk_category,
        "keywords_found": found_pos + found_neg,
        "sentiment_score": round(sentiment_score, 2),
        "delta": delta
    }

def generate_summary(inputs: dict, adjusted_score: int, delta: int) -> str:
    """
    Generates the exact summary string specified.
    """
    cap = inputs.get("capacity_utilization")
    site = inputs.get("site_visit_outcome") or "UNKNOWN"
    mgt = inputs.get("management_quality") or "UNKNOWN"
    promoter = inputs.get("promoter_cooperation") or "UNKNOWN"
    litigation = inputs.get("pending_litigation", False)
    industry = inputs.get("industry_outlook") or "UNKNOWN"
    
    sentences = []
    
    # S1
    if cap is not None:
        sentences.append(f"Plant capacity utilization was reported at {cap}%, with a {site.lower()} site visit outcome.")
    else:
        sentences.append(f"Site visit outcome was {site.lower()}; capacity utilization data was not provided.")
        
    # S2
    sentences.append(f"Management quality was assessed as {mgt.lower()}, with {promoter.lower()} promoter cooperation during due diligence.")
    
    # S3
    if litigation and industry == "ADVERSE":
        sentences.append("Active litigation presents contingent liability risk, compounded by an adverse industry outlook.")
    elif litigation:
        sentences.append("Active litigation was noted, presenting contingent liability risk.")
    elif industry == "ADVERSE":
        sentences.append("The prevailing industry outlook is adverse, posing headwind risks.")
    else:
        sentences.append(f"No litigation was reported and industry conditions are {industry.lower()}.")
        
    # S4
    sentences.append(f"A qualitative adjustment of {delta} points was applied, resulting in an adjusted score of {adjusted_score}/100.")
    
    return " ".join(sentences)

def compute_qualitative_delta(base_score: float, inputs: dict) -> dict:
    """
    Computes qualitative adjustments to the base score based on structural flags.
    """
    raw_delta = 0
    breakdown = {}
    
    cap = inputs.get("capacity_utilization")
    if cap is not None:
        if cap < 30:
            raw_delta -= 20
            breakdown["capacity"] = -20
        elif 30 <= cap <= 50:
            raw_delta -= 10
            breakdown["capacity"] = -10
        elif cap > 80:
            raw_delta += 8
            breakdown["capacity"] = 8
            
    mgt = inputs.get("management_quality")
    if mgt == "WEAK":
        raw_delta -= 15
        breakdown["management"] = -15
    elif mgt == "AVERAGE":
        raw_delta -= 5
        breakdown["management"] = -5
    elif mgt == "STRONG":
        raw_delta += 8
        breakdown["management"] = 8
        
    site = inputs.get("site_visit_outcome")
    if site == "NEGATIVE":
        raw_delta -= 12
        breakdown["site_visit"] = -12
    elif site == "NEUTRAL":
        raw_delta -= 4
        breakdown["site_visit"] = -4
    elif site == "POSITIVE":
        raw_delta += 8
        breakdown["site_visit"] = 8
        
    if inputs.get("pending_litigation") is True:
        raw_delta -= 18
        breakdown["litigation"] = -18
        
    industry = inputs.get("industry_outlook")
    if industry == "ADVERSE":
        raw_delta -= 8
        breakdown["industry"] = -8
    elif industry == "FAVORABLE":
        raw_delta += 6
        breakdown["industry"] = 6
        
    collat = inputs.get("collateral_quality")
    if collat == "SUBSTANDARD":
        raw_delta -= 10
        breakdown["collateral"] = -10
    elif collat == "STANDARD":
        raw_delta -= 3
        breakdown["collateral"] = -3
    elif collat == "PRIME":
        raw_delta += 5
        breakdown["collateral"] = 5
        
    prom = inputs.get("promoter_cooperation")
    if prom == "LOW":
        raw_delta -= 10
        breakdown["promoter"] = -10
    elif prom == "MEDIUM":
        raw_delta -= 4
        breakdown["promoter"] = -4
    elif prom == "HIGH":
        raw_delta += 5
        breakdown["promoter"] = 5
        
    # Free Text NLP
    nlp_result = classify_free_text(inputs.get("free_text_notes", ""))
    raw_delta += nlp_result["delta"]
    breakdown["free_text_nlp"] = nlp_result["delta"]
    
    # Store intermediate value before clamping
    uncapped_delta = raw_delta
    
    # Cap Delta
    final_delta = max(-30, min(15, raw_delta))
    
    # Generate Adjusted Score and clamp
    adjusted_score = max(0, min(100, int(base_score + final_delta)))
    
    # Risk Tier
    if adjusted_score >= 70:
        risk_tier = "APPROVE"
    elif adjusted_score >= 50:
        risk_tier = "WATCHLIST"
    else:
        risk_tier = "REJECT"
        
    # Generate Paragraph
    summary_paragraph = generate_summary(inputs, adjusted_score, final_delta)

    return {
        "base_score": base_score,
        "uncapped_delta": uncapped_delta,
        "final_delta": final_delta,
        "adjusted_score": adjusted_score,
        "risk_tier": risk_tier,
        "nlp_analysis": nlp_result,
        "breakdown": breakdown,
        "summary_paragraph": summary_paragraph
    }


if __name__ == "__main__":
    # INLINE TEST
    test_payload = {
        "base_score": 68,
        "capacity_utilization": 40,
        "management_quality": "AVERAGE",
        "site_visit_outcome": "NEUTRAL",
        "pending_litigation": True,
        "industry_outlook": "STABLE",
        "collateral_quality": "STANDARD",
        "promoter_cooperation": "MEDIUM",
        "free_text_notes": "Factory found idle in second shift. Some dispute with workers noted. Order book looks healthy."
    }
    
    print("\n--- QUALITATIVE ADJUSTER TEST ---")
    result = compute_qualitative_delta(test_payload["base_score"], test_payload)
    
    import json
    print(json.dumps(result, indent=2))

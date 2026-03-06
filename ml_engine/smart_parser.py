import re

ANCHORS = {
    "GST_RETURN": ["gstin", "gstr-3b", "outward supplies", "itc"],
    "BANK_STATEMENT": ["account number", "closing balance", "transaction date", "debit", "credit"],
    "ANNUAL_REPORT": ["chairman", "board of directors", "auditor", "annual report"],
    "SANCTION_LETTER": ["sanctioned amount", "rate of interest", "collateral", "facility"],
    "LEGAL_NOTICE": ["plaintiff", "defendant", "court", "petition", "respondent"],
    "BALANCE_SHEET": ["total assets", "total liabilities", "shareholders equity", "balance sheet"]
}

def classify_document_type(text: str, filename: str = "") -> dict:
    """
    Classify document based on anchor phrases.
    """
    if not text:
        return {"document_type": "UNKNOWN", "confidence": 0.0}
        
    text_lower = text.lower()
    
    best_type = "UNKNOWN"
    max_score = 0
    best_confidence = 0.0
    
    for doc_type, anchors in ANCHORS.items():
        matches = sum(1 for anchor in anchors if anchor in text_lower)
        if matches > 0:
            confidence = matches / len(anchors)
            if matches > max_score:
                max_score = matches
                best_type = doc_type
                best_confidence = confidence
                
    return {
        "document_type": best_type,
        "confidence": round(best_confidence, 2)
    }

def parse_by_type(pdf_path: str, doc_type: str) -> dict:
    """
    Specialized parsing logic based on document type.
    """
    if doc_type == "BANK_STATEMENT":
        return {
            "transactions": [], 
            "opening_balance": 0.0, 
            "closing_balance": 0.0, 
            "total_credits": 0.0, 
            "total_debits": 0.0, 
            "period": ""
        }
    elif doc_type == "ANNUAL_REPORT":
        return {
            "financials_by_year": {}, 
            "key_ratios": {}, 
            "auditor_opinion": ""
        }
    elif doc_type == "GST_RETURN":
        return {
            "turnover": 0.0, 
            "output_tax": 0.0, 
            "itc_claimed": 0.0, 
            "filing_period": ""
        }
    elif doc_type == "SANCTION_LETTER":
        return {
            "existing_facilities": [], 
            "total_existing_exposure": 0.0
        }
    elif doc_type == "LEGAL_NOTICE":
        return {
            "legal_proceedings": []
        }
    elif doc_type == "BALANCE_SHEET":
        return {
            "balance_sheet_items": {}
        }
    return {}

def multi_document_reconcile(parsed_docs: list) -> dict:
    """
    Cross-reference after all docs parsed.
    """
    # Placeholder reconciliation logic based on requirements
    consistency_score = 100
    cross_document_flags = []
    
    # Needs actual parsed document logic to implement checks
    # E.g. Annual report revenue vs bank statement credits
    # Sanction letter existing loans vs balance sheet debt
    
    return {
        "consistency_score": consistency_score,
        "cross_document_flags": cross_document_flags,
        "merged_financials": {}
    }


if __name__ == "__main__":
    import json
    text1 = "GSTIN: 27AAPCS1234F1Z5. GSTR-3B Return. Outward taxable supplies: 12,50,000"
    text2 = "Account Number: 1234567890. Closing Balance: 45,230.00. Transaction Date: 01-Jan-2025. Debit: 5000 Credit: 12000"
    text3 = "The plaintiff hereby files this petition before the Hon'ble Court against the defendant for recovery"

    print(json.dumps({
        "text1": classify_document_type(text1),
        "text2": classify_document_type(text2),
        "text3": classify_document_type(text3)
    }, indent=2))

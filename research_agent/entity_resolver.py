"""
Entity resolver module to standardize target companies and link evidence directly.
"""
from typing import List, Dict
from rapidfuzz import process, fuzz

def match_articles_to_entities(evidence_list: List[Dict], master_entities: List[str]) -> List[Dict]:
    """
    Match fetched articles to the given NLP-extracted entities (e.g., ORG or Promoter names).
    Output structure includes confidence and tags based on keyword overlap.
    """
    resolved_evidence = []
    
    # Common risk keywords to tag
    risk_keywords = ["litigation", "npa", "default", "scam", "fraud", "debt", "insolvency", "court", "rbi"]

    for article in evidence_list:
        combined_text = (article.get("title", "") + " " + article.get("content", "")).lower()
        
        # Determine highest match among master entities
        best_match = None
        best_score = 0
        
        if master_entities:
            # Match against title for strongest signal, but fall back to combined text
            result = process.extractOne(article.get("title", ""), master_entities, scorer=fuzz.token_set_ratio)
            if result:
                match_name, score, _ = result
                best_match = match_name
                best_score = score
        
        # Look for Tags
        tags = []
        for kw in risk_keywords:
            if kw in combined_text:
                tags.append(kw.upper())
                
        # We enforce a generic confidence score based on the entity match
        resolved_evidence.append({
            "article": article,
            "matched_entity": best_match if best_score > 60 else None,
            "confidence": round(best_score, 2),
            "tags": tags
        })

    return resolved_evidence

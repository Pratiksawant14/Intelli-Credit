"""
Entity linking and fuzzy matching (for promoters, PAN/CINs).
"""
from typing import List, Dict
from rapidfuzz import process, fuzz

def link_entities(extracted_entities: List[Dict], master_db: List[Dict]) -> List[Dict]:
    """
    Uses fuzzy logic to match extracted entities (ORG / PERSON) with a master database.
    
    Returns enriched list of entities with match information.
    Example return:
    [
        { "type": "ORG", "text": "Orbit Holdings Ltd.", "match": "Orbit Holdings Pvt Ltd", "score": 92.0, "cin": "..." }
    ]
    """
    enriched_entities = []
    
    # Pre-extract master names for rapidfuzz
    master_orgs = []
    master_org_map = {}
    master_persons = []
    master_person_map = {}
    
    for record in master_db:
        if record.get("type", "ORG") == "ORG":
            name = record.get("name")
            if name:
                master_orgs.append(name)
                master_org_map[name] = record
        elif record.get("type") == "PERSON":
            name = record.get("name")
            if name:
                master_persons.append(name)
                master_person_map[name] = record

    for ent in extracted_entities:
        ent_type = ent.get("type")
        ent_text = ent.get("text")
        
        # Base entity dict
        enriched_ent = {"type": ent_type, "text": ent_text}
        
        if ent_type == "ORG" and master_orgs:
            # Fuzzy match for ORG
            result = process.extractOne(ent_text, master_orgs, scorer=fuzz.WRatio)
            if result:
                match_name, score, _ = result
                # Add match threshold (e.g., 80)
                if score >= 80:
                    matched_record = master_org_map[match_name]
                    enriched_ent["match"] = match_name
                    enriched_ent["score"] = round(score, 2)
                    # Add extra metadata like CIN if available
                    if "cin" in matched_record:
                        enriched_ent["cin"] = matched_record["cin"]
                        
        elif ent_type == "PERSON" and master_persons:
            # Fuzzy match for PERSON
            result = process.extractOne(ent_text, master_persons, scorer=fuzz.WRatio)
            if result:
                match_name, score, _ = result
                if score >= 80:
                    matched_record = master_person_map[match_name]
                    enriched_ent["match"] = match_name
                    enriched_ent["score"] = round(score, 2)
                    if "id" in matched_record:
                        enriched_ent["id"] = matched_record["id"]
                    
        # Merge other matched regex type information where relevant 
        # (For this scope, we just append whatever didn't match fuzzy logic perfectly)
        enriched_entities.append(enriched_ent)
        
    return enriched_entities

# Helper to test the logic implementation
if __name__ == "__main__":
    test_input = [
        { "type": "PERSON", "text": "Rakesh Mehta" },
        { "type": "ORG", "text": "Orbit Holdings Ltd." },
        { "type": "MONEY", "text": "₹4 Cr" },
        { "type": "DATE", "text": "Jan 22, 2023" },
        { "type": "GSTIN", "text": "27ABCDE1234F2Z6" }
    ]
    
    master_db = [
        {"type": "ORG", "name": "Orbit Holdings Pvt Ltd", "cin": "L12345MH2013PLC000123"},
        {"type": "PERSON", "name": "Rakesh S. Mehta", "id": "DIR9988"}
    ]
    
    linked = link_entities(test_input, master_db)
    import json
    print(json.dumps(linked, indent=2))

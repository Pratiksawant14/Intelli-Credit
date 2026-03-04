# test_research.py
from research_agent.crawler import fetch_evidence_for_entity
from research_agent.entity_resolver import match_articles_to_entities
from research_agent.evidence_indexer import index_evidence, query_evidence
import json

def run_test():
    company = "Orbit Holdings"
    print(f"1. Fetching Evidence for {company}...")
    # Using generic keywords to get some hits on Google News
    evidence = fetch_evidence_for_entity(company, ["NPA", "court", "fund", "loss", "profit"])
    print(f"Found {len(evidence)} articles.")
    if evidence:
        print("Sample:", evidence[0]["title"])
        
    print("\n2. Entity Linking Articles...")
    # Resolving them with master entity list
    resolved = match_articles_to_entities(evidence, ["Orbit Holdings Pvt Ltd"])
    for res in resolved:
        if res["matched_entity"]:
            print(f"Matched '{res['matched_entity']}' with confidence {res['confidence']}")
            break # Just print one
            
    print("\n3. Indexing Evidence in FAISS...")
    index_evidence(company, resolved)
    
    print("\n4. Querying Evidence ('legal default')...")
    results = query_evidence(company, "legal default")
    
    # Strip some massive content fields for logging
    clean_results = []
    for r in results:
        r_clone = dict(r)
        r_clone['article']['content'] = str(r_clone['article']['content'])[:50] + "..."
        clean_results.append(r_clone)
        
    print(json.dumps(clean_results, indent=2))

if __name__ == "__main__":
    run_test()

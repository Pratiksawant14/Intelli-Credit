"""
FastAPI routes for retrieving evidence from embeddings.
"""
from fastapi import APIRouter
from research_agent.crawler import fetch_evidence_for_entity
from research_agent.entity_resolver import match_articles_to_entities
from research_agent.evidence_indexer import index_evidence, query_evidence

router = APIRouter()

@router.get("/evidence/")
async def get_evidence(entity_name: str, query: str = ""):
    """
    Fetches online evidence, resolves it against the entity, indexes it, 
    and returns relevant search results based on the query.
    """
    keywords = ["NPA", "court", "rbi", "default", "scam"]
    
    # 1. Fetch
    raw_evidence = fetch_evidence_for_entity(entity_name, keywords)
    
    # 1.5 MOCK DATA INJECTION FOR TESTING "Orbit Holdings"
    if not raw_evidence and "Orbit" in entity_name:
        raw_evidence = [
            {
                "title": "Orbit Holdings Pvt Ltd declared NPA by SBI",
                "date": "2026-03-01",
                "source": "Financial Times Mock",
                "url": "https://example.com/mock/orbit-npa",
                "content": "State Bank of India has initiated insolvency proceedings against Orbit Holdings Pvt Ltd due to multiple missed EMI payments. This constitutes a severe default under the Bankruptcy Code."
            },
            {
                "title": "Promoters of Orbit under legal scanner for loan fraud",
                "date": "2026-02-15",
                "source": "Economic Journal Mock",
                "url": "https://example.com/mock/orbit-fraud",
                "content": "Director Rahul Sharma is facing scrutiny from the RBI after allegations of a massive loan scam connected to Orbit Holdings' operations."
            }
        ]

    # 2. Resolve/Tag
    resolved_evidence = match_articles_to_entities(raw_evidence, [entity_name])
    
    # 3. Index
    index_evidence(entity_name, resolved_evidence)
    
    # 4. Query DB if specific query provided, otherwise return all mapped
    if query:
        resolved_results = query_evidence(entity_name, query, top_k=5)
    else:
        # Return all that successfully matched the entity or have risk tags
        resolved_results = [e for e in resolved_evidence if e["matched_entity"] or e["tags"]]
        
    # Flatten structure so React frontend can read `.title`, `.url`, etc directly
    final_results = []
    for item in resolved_results:
        flat_item = item.get("article", {}).copy()
        flat_item["tags"] = item.get("tags", [])
        flat_item["matched_entity"] = item.get("matched_entity")
        if "search_distance" in item:
            flat_item["search_distance"] = item["search_distance"]
        final_results.append(flat_item)
        
    return {"entity": entity_name, "results": final_results}

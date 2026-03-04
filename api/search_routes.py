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
    
    # 2. Resolve/Tag
    resolved_evidence = match_articles_to_entities(raw_evidence, [entity_name])
    
    # 3. Index
    index_evidence(entity_name, resolved_evidence)
    
    # 4. Query DB if specific query provided, otherwise return all mapped
    if query:
        results = query_evidence(entity_name, query, top_k=5)
    else:
        # Return all that successfully matched the entity or have risk tags
        results = [e for e in resolved_evidence if e["matched_entity"] or e["tags"]]
        
    return {"entity": entity_name, "results": results}

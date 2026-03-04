"""
Embeddings and retrieval storage integration using sentence-transformers and FAISS/Pinecone.
"""
from typing import List, Dict
import numpy as np
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
from sentence_transformers import SentenceTransformer

# Load model globally to avoid reloading overhead per call
try:
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Failed to load SentenceTransformer: {e}")
    embedding_model = None

# In-memory generic store for demo (Ideally Pinecone or persisted FAISS)
IN_MEMORY_DB = []
IN_MEMORY_INDEX = None

def index_evidence(entity_name: str, evidence_list: List[Dict]) -> None:
    """
    Generate embeddings of article content and upsert into vector database.
    Because we don't have Pinecone instantly available during this phase, 
    we use a mock FAISS in-memory index + basic storage array.
    """
    global IN_MEMORY_DATABASE, IN_MEMORY_INDEX
    
    if not embedding_model or not FAISS_AVAILABLE:
        print("Embeddings model or FAISS not available. Skipping true indexing.")
        return
        
    for item in evidence_list:
        article = item.get("article", {})
        text_to_embed = f"{article.get('title', '')} {article.get('content', '')}"
        
        if not text_to_embed.strip():
            continue
            
        vector = embedding_model.encode(text_to_embed)
        
        # Add to local FAISS index if initializing
        if IN_MEMORY_INDEX is None:
            dimension = vector.shape[0]
            IN_MEMORY_INDEX = faiss.IndexFlatL2(dimension)
            
        vector_np = np.array([vector], dtype=np.float32)
        IN_MEMORY_INDEX.add(vector_np)
        
        # Save metadata reference
        IN_MEMORY_DB.append({
            "entity": entity_name,
            "evidence": item, # fully resolved chunk
            "vector_id": len(IN_MEMORY_DB)
        })
        
    print(f"Indexed {len(evidence_list)} articles for {entity_name}")

def query_evidence(entity_name: str, query: str, top_k: int = 3) -> List[Dict]:
    """
    Search function to retrieve top k related articles based on sentence similarity.
    """
    if not embedding_model or not FAISS_AVAILABLE or IN_MEMORY_INDEX is None:
        return []
        
    query_vector = embedding_model.encode(query)
    query_np = np.array([query_vector], dtype=np.float32)
    
    # Perform Search
    distances, indices = IN_MEMORY_INDEX.search(query_np, min(top_k, len(IN_MEMORY_DB)))
    
    results = []
    for i, idx in enumerate(indices[0]):
        if idx == -1: continue # No more results
        
        # Retrieve mapped metadata
        record = IN_MEMORY_DB[idx]
        # Could filter by entity_name here if needed
        # if record["entity"] != entity_name: continue
        
        result_item = record["evidence"]
        # Inject the retrieval score
        result_item["search_distance"] = round(float(distances[0][i]), 4)
        results.append(result_item)
        
    return results

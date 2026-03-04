"""
Prefect flow: web research (Scrapy/feedparser) -> index evidence (Pinecone/FAISS)
"""
from prefect import flow, task
from typing import List

from research_agent.crawler import fetch_evidence_for_entity
from research_agent.entity_resolver import match_articles_to_entities
from research_agent.evidence_indexer import index_evidence

@task
def run_crawlers(entity_name: str, keywords: List[str]):
    print(f"Running crawler for {entity_name}...")
    return fetch_evidence_for_entity(entity_name, keywords)

@task
def index_evidence_task(entity_name: str, raw_evidence: list):
    print(f"Indexing evidence for {entity_name}...")
    resolved = match_articles_to_entities(raw_evidence, [entity_name])
    index_evidence(entity_name, resolved)
    return resolved

@flow
def web_research_flow(entity_name: str, keywords: List[str] = ["NPA", "court", "rbi", "default", "lawsuit"]):
    raw = run_crawlers(entity_name, keywords)
    resolved = index_evidence_task(entity_name, raw)
    return resolved

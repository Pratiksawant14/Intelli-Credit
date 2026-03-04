"""
Prefect flow: document OCR -> NLP entity extraction -> Feature engineering
"""
from prefect import flow, task
import json

from ocr_pipeline.pdf_parser import extract_layout_text
from ocr_pipeline.table_extractor import extract_tables
from nlp_module.ner_extractor import extract_entities
from ml_engine.features import extract_features

@task
def parse_document(file_path: str):
    print(f"Parsing document: {file_path}")
    text_blocks = extract_layout_text(file_path)
    tables = extract_tables(file_path)
    # Convert text blocks to simple raw text for NLP
    raw_text = " ".join([b.get("text", "") for b in text_blocks])
    
    return {
        "text_blocks": text_blocks,
        "tables": [t.to_dict() for t in tables],
        "raw_text": raw_text
    }

@task
def extract_nlp(raw_text: str):
    print("Extracting NLP Entities...")
    return extract_entities(raw_text)

@task
def engineer_features(document_data: dict, nlp_entities: list):
    print("Engineering ML features...")
    # Map document tables/blocks into a simple flattened dict for features extraction
    # This is a simplification; in production, you'd properly map keys 
    mock_flattened_doc = {"extracted_revenue": 1000000} 
    df = extract_features(mock_flattened_doc, nlp_entities)
    return df

@flow
def ocr_to_features_flow(doc_path: str):
    doc_data = parse_document(doc_path)
    entities = extract_nlp(doc_data["raw_text"])
    features_df = engineer_features(doc_data, entities)
    return features_df

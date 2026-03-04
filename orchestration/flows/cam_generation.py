"""
Prefect flow: LLM draft generation -> Template build -> PDF Output
"""
from prefect import flow, task
from typing import Dict, Any

from cam_generator.llm_generator import generate_summaries
from cam_generator.template_builder import render_cam_to_pdf

@task
def generate_llm_draft(payload: Dict[str, Any]):
    print("Generating LLM Draft Summaries...")
    return generate_summaries(payload)

@task
def render_template(cam_data: dict, file_name: str):
    print("Rendering final CAM PDF...")
    render_cam_to_pdf(cam_data, file_name)
    return file_name

@flow
def cam_generation_flow(payload: Dict[str, Any]):
    summaries = generate_llm_draft(payload)
    
    # Merge payload specific to CAM formatting (this matches our cam_routes API endpoint structure mapping)
    cam_data = {
        "company_name": payload.get("company_name", "Unknown Company"),
        "date": payload.get("date", "Unknown Date"),
        "entity_id": payload.get("entity_id", "Unknown ID"),
        
        "revenue": payload.get("features", {}).get("revenue", 0),
        "working_capital": payload.get("features", {}).get("working_capital", 0),
        "debt_equity": payload.get("features", {}).get("debt_equity", 0),
        
        "risk_score": payload.get("ml_output", {}).get("predicted_score", "N/A"),
        "decision": payload.get("ml_output", {}).get("decision", "Unknown"),
        "top_features": payload.get("ml_output", {}).get("top_features", []),
        
        "character_summary": summaries["character_summary"],
        "conditions_summary": summaries["conditions_summary"],
        "recommendation": summaries["recommendation"],
        
        "evidence_snippets": payload.get("evidence", [])
    }
    
    output_path = f"generated_cams/FlowOutput_{cam_data['company_name'].replace(' ','')}.pdf"
    
    file_path = render_template(cam_data, output_path)
    return file_path

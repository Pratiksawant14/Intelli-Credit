"""
FastAPI routes to generate Credit Appraisal Memo (CAM).
"""
from fastapi import APIRouter
from fastapi.responses import FileResponse
from typing import Dict, Any
import os

from cam_generator.llm_generator import generate_summaries
from cam_generator.template_builder import render_cam_to_pdf

router = APIRouter()
REPORTS_DIR = "generated_cams"
os.makedirs(REPORTS_DIR, exist_ok=True)

@router.post("/generate-cam/")
async def generate_cam(payload: Dict[str, Any]):
    """
    Input: features, NLP flags, score, SHAP, evidence
    Generates LLM summaries, renders PDF via ReportLab, and returns file download link.
    """
    # 1. Generate Summaries via LLM (or fallback)
    summaries = generate_summaries(payload)
    
    # 2. Merge Payload with Summaries
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
    
    company_safe_name = cam_data["company_name"].replace(" ", "_").replace("/", "")
    output_filename = f"CAM_{company_safe_name}.pdf"
    output_path = os.path.join(REPORTS_DIR, output_filename)
    
    # 3. Render PDF
    render_cam_to_pdf(cam_data, output_path)
    
    # Return as physical file download
    return FileResponse(path=output_path, filename=output_filename, media_type='application/pdf')

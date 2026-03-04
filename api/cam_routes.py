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
        
        "notes": payload.get("notes", ""),
        
        "evidence_snippets": payload.get("evidence", [])
    }
    
    company_safe_name = cam_data["company_name"].replace(" ", "_").replace("/", "")
    output_filename = f"CAM_{company_safe_name}.pdf"
    output_path = os.path.join(REPORTS_DIR, output_filename)
    
    # 3. Render PDF
    render_cam_to_pdf(cam_data, output_path)
    
    # 4. Save to Postgres DB
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if supabase_url and supabase_key:
            from supabase import create_client, Client
            supabase: Client = create_client(supabase_url, supabase_key)
            
            # Map values explicitly, fallback handles missing dictionary keys safely.
            # Handle possible string formatting in score
            score_val = str(cam_data.get("risk_score", 0))
            if not score_val.replace('.', '', 1).isdigit():
                score_val = "0"
                
            supabase.table("cam_reports").insert({
                "company_name": cam_data["company_name"],
                "credit_score": float(score_val),
                "disposition": cam_data["decision"],
                "pdf_path": output_path,
                "analyst_notes": cam_data.get("notes", ""),
                "user_id": payload.get("user_id")
            }).execute()
            print("Successfully saved CAM Generation to History logs.")
    except Exception as e:
        print(f"Failed to log CAM to History Table: {e}")
        
    # Return as physical file download
    return FileResponse(path=output_path, filename=output_filename, media_type='application/pdf')

@router.get("/history/")
async def fetch_cam_history(user_id: str = None):
    """Returns the most recent 10 generated CAMs from Supabase."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    if supabase_url and supabase_key:
        try:
            from supabase import create_client, Client
            supabase: Client = create_client(supabase_url, supabase_key)
            query = supabase.table("cam_reports").select("*")
            if user_id:
                query = query.eq("user_id", user_id)
            result = query.order("generated_at", desc=True).limit(10).execute()
            return result.data
        except Exception as e:
            print(f"Failed retrieving CAM history: {e}")
            return []
    return []

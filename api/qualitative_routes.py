"""
FastAPI routes for Qualitative Inputs & NLP Score Adjustment.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ml_engine.qualitative_adjuster import compute_qualitative_delta

router = APIRouter()

# Input schemas exactly mapping the qualitative form
class QualitativeInput(BaseModel):
    capacity_utilization: Optional[float] = None
    management_quality: Optional[str] = None
    site_visit_outcome: Optional[str] = None
    pending_litigation: Optional[bool] = None
    industry_outlook: Optional[str] = None
    collateral_quality: Optional[str] = None
    promoter_cooperation: Optional[str] = None
    free_text_notes: Optional[str] = ""

class QualitativePayload(BaseModel):
    base_score: float
    company_name: str
    inputs: QualitativeInput

class NLPAnalysis(BaseModel):
    risk_category: str
    keywords_found: list
    sentiment_score: float
    delta: int

class QualitativeResponse(BaseModel):
    company_name: str
    base_score: float
    uncapped_delta: int
    final_delta: int
    adjusted_score: int
    risk_tier: str
    nlp_analysis: NLPAnalysis
    breakdown: dict
    summary_paragraph: str

@router.post("/adjust/", response_model=QualitativeResponse)
async def adjust_qualitative_score(payload: QualitativePayload):
    try:
        # compute_qualitative_delta expects the base_score and a dict of the inputs
        result = compute_qualitative_delta(
            base_score=payload.base_score,
            inputs=payload.inputs.model_dump()
        )
        
        # Merge company_name into result for response
        result["company_name"] = payload.company_name
        
        return QualitativeResponse(**result)
        
    except Exception as e:
        print(f"Qualitative adjustment error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process qualitative adjustment.")

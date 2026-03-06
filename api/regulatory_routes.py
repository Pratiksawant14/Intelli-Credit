from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from research_agent.regulatory_crawler import aggregate_regulatory_intelligence

router = APIRouter()

class RegulatoryRequest(BaseModel):
    company_name: str
    cin: Optional[str] = None
    promoter_names: Optional[List[str]] = []

class RegulatoryFlag(BaseModel):
    source: str
    date: str
    type: str
    severity: str
    detail: str
    source_url: str
    scraped_at: str

class RegulatoryResponse(BaseModel):
    regulatory_risk_score: int
    critical_flags: List[RegulatoryFlag]
    warnings: List[RegulatoryFlag]
    clean_checks: List[RegulatoryFlag]
    sources_checked: List[str]
    summary_paragraph: str

@router.post("/check", response_model=RegulatoryResponse)
async def check_regulatory_intelligence(payload: RegulatoryRequest):
    try:
        # aggregate_regulatory_intelligence handles its own concurrency and fault tolerance
        result = await aggregate_regulatory_intelligence(
            company_name=payload.company_name,
            cin=payload.cin,
            promoter_names=payload.promoter_names
        )
        return RegulatoryResponse(**result)
    except Exception as e:
        print(f"Error in regulatory check: {e}")
        raise HTTPException(status_code=500, detail="Failed to run regulatory intelligence check.")

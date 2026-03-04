from cam_generator.llm_generator import generate_summaries
from cam_generator.template_builder import render_cam_to_pdf
import datetime

def run_test():
    # Simulated input data combining OCR, NLP, ML, and Research outputs
    input_data = {
        "features": {
            "revenue": 1000000,
            "working_capital": 200000,
            "debt_equity": 0.5
        },
        "ml_output": {
            "predicted_score": 0.5,
            "decision": "Watchlist",
            "top_features": [
                {"feature": "gst_bank_match_score", "value": 0.95, "impact": -0.05},
                {"feature": "legal_flag_count", "value": 3.0, "impact": 0.15}
            ]
        },
        "entity_data": [
            {"type": "LAW", "text": "NPA flag on past loan"},
            {"type": "PERSON", "text": "Rakesh Mehta"}
        ],
        "research": [
            {
                "title": "Orbit Holdings faces court case over debt delays",
                "tags": ["NPA", "litigation"],
                "content": "A recent high court case..."
            }
        ]
    }

    print("1. Generating Summaries (via LLM or Rules fallback)...")
    summaries = generate_summaries(input_data)
    
    # Merge all into one context dictionary for the PDF template
    cam_data = {
        "company_name": "Orbit Holdings Pvt Ltd",
        "date": datetime.date.today().strftime("%Y-%m-%d"),
        "entity_id": "CIN: L12345MH2013PLC000123",
        "revenue": input_data["features"]["revenue"],
        "working_capital": input_data["features"]["working_capital"],
        "debt_equity": input_data["features"]["debt_equity"],
        "risk_score": input_data["ml_output"]["predicted_score"],
        "decision": input_data["ml_output"]["decision"],
        "top_features": input_data["ml_output"]["top_features"],
        "character_summary": summaries["character_summary"],
        "conditions_summary": summaries["conditions_summary"],
        "recommendation": summaries["recommendation"],
        "evidence_snippets": [
            {
                "source": "Google News Tracking", 
                "content": "Litigation flags regarding debt delays detected."
            }
        ]
    }

    print("2. Rendering CAM to PDF using ReportLab...")
    render_cam_to_pdf(cam_data, "CAM_Report.pdf")
    
if __name__ == "__main__":
    run_test()

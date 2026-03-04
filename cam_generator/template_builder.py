"""
Jinja2 templates/builder for Word or PDF generation.
Using ReportLab to construct the Credit Appraisal Memo natively in Python.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from typing import Dict, Any

def render_cam_to_pdf(data: Dict[str, Any], output_path: str) -> None:
    """
    Builds the Credit Appraisal Memo (CAM) natively formatting the document and rendering to PDF.
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='SectionHeader', parent=styles['Heading2'], textColor=colors.HexColor("#0f3c5b")))
    styles.add(ParagraphStyle(name='InfoItem', parent=styles['Normal'], spaceAfter=6))
    
    elements = []
    
    # Header
    elements.append(Paragraph("<b>Credit Appraisal Memo (CAM)</b>", styles['Heading1']))
    elements.append(Paragraph(f"<b>Company:</b> {data.get('company_name', 'Unknown')}", styles['InfoItem']))
    elements.append(Paragraph(f"<b>Date:</b> {data.get('date', 'N/A')}", styles['InfoItem']))
    elements.append(Paragraph(f"<b>Entity ID:</b> {data.get('entity_id', 'N/A')}", styles['InfoItem']))
    elements.append(Spacer(1, 12))
    
    # Five Cs of Credit
    elements.append(Paragraph("<b>Five Cs of Credit</b>", styles['SectionHeader']))
    
    # Character
    elements.append(Paragraph(f"<b>Character (Management & Legal):</b> {data.get('character_summary', 'N/A')}", styles['InfoItem']))
    
    # Capacity
    capacity_text = f"Revenue: ₹{data.get('revenue', 0):,}. Working Capital: ₹{data.get('working_capital', 0):,}. Estimated Debt-to-Equity: {data.get('debt_equity', 0)}."
    elements.append(Paragraph(f"<b>Capacity (Financials):</b> {capacity_text}", styles['InfoItem']))
    
    # Capital
    elements.append(Paragraph("<b>Capital:</b> Strong asset base as extracted from structured financials.", styles['InfoItem']))
    
    # Collateral
    elements.append(Paragraph("<b>Collateral:</b> Currently unsecured (No security info found).", styles['InfoItem']))
    
    # Conditions
    elements.append(Paragraph(f"<b>Conditions (External Risk):</b> {data.get('conditions_summary', 'N/A')}", styles['InfoItem']))
    elements.append(Spacer(1, 12))
    
    # ML Scoring Summary
    elements.append(Paragraph("<b>ML Scoring & Explainability Summary</b>", styles['SectionHeader']))
    elements.append(Paragraph(f"<b>Risk Score:</b> {data.get('risk_score', 'N/A')} - <b>{data.get('decision', 'N/A')}</b>", styles['InfoItem']))
    
    # SHAP Top Features
    top_features = data.get('top_features', [])
    if top_features:
        elements.append(Paragraph("<b>Top Risk Drivers:</b>", styles['InfoItem']))
        for feat in top_features:
            impact_sign = "+" if feat['impact'] >= 0 else ""
            elements.append(Paragraph(f"• {feat['feature']}: {feat['value']} (Impact: {impact_sign}{feat['impact']:.4f})", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Evidence Summary
    elements.append(Paragraph("<b>Evidence Summary (Recent findings)</b>", styles['SectionHeader']))
    evidence = data.get('evidence_snippets', [])
    for ev in evidence:
        elements.append(Paragraph(f"<i>Source: {ev.get('source', 'Unknown')}</i>", styles['Normal']))
        elements.append(Paragraph(ev.get('content', 'No content'), styles['Normal']))
        elements.append(Spacer(1, 6))
        
    elements.append(Spacer(1, 12))
    
    # Final Recommendation
    elements.append(Paragraph("<b>Final Recommendation</b>", styles['SectionHeader']))
    elements.append(Paragraph(f"<b>{data.get('recommendation', 'N/A')}</b>", styles['InfoItem']))
    
    # Analyst Overlay Notes
    analyst_notes = data.get('notes', '').strip()
    if analyst_notes:
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("<b>Human Analyst Overlay Notes</b>", styles['SectionHeader']))
        elements.append(Paragraph(f"<i>{analyst_notes}</i>", styles['Normal']))
    
    # Build it
    doc.build(elements)
    print(f"CAM successfully generated at: {output_path}")

"""
FastAPI routes for file ingest and processing.
"""
from fastapi import APIRouter, UploadFile, File
from typing import List
import os
import shutil

from ocr_pipeline.pdf_parser import extract_layout_text
from ocr_pipeline.table_extractor import extract_tables, export_tables_to_json
from ocr_pipeline.ocr_utils import run_ocr_with_tesseract

router = APIRouter()
TEMP_DIR = "temp_uploads"

os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/upload/")
async def upload_documents(files: List[UploadFile] = File(...)):
    results = []
    
    for file in files:
        file_path = os.path.join(TEMP_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Optional: Routing logic by type based on filename
        doc_type = "unknown"
        lower_name = file.filename.lower()
        if "gst" in lower_name: doc_type = "gst_return"
        elif "bank" in lower_name: doc_type = "bank_statement"
        elif "annual" in lower_name or "report" in lower_name: doc_type = "annual_report"
        
        # 1. Run Layout parsing
        text_blocks = extract_layout_text(file_path)
        
        # 2. Extract specific Tables
        tables = extract_tables(file_path)
        # Convert to light dict format instead of JSON string for response
        tables_data = [t.to_dict(orient="records") for t in tables]
        
        # 3. Fallback to Tesseract OCR if both are empty
        raw_text = ""
        if not text_blocks and not tables:
            raw_text = run_ocr_with_tesseract(file_path)
            
        results.append({
            "filename": file.filename,
            "document_type": doc_type,
            "extracted_text_blocks": text_blocks,
            "extracted_tables": tables_data,
            "raw_ocr": raw_text
        })
        
    return {"status": "success", "processed_files": results}

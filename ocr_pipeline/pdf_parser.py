import fitz  # PyMuPDF
from langdetect import detect, detect_langs

def extract_layout_text(pdf_path: str) -> list:
    """
    Extracts text by block/paragraph from a PDF using PyMuPDF (fitz)
    and returns a list of structured blocks.
    
    Output format example:
    [
        {
          "page": 1,
          "bbox": [x0, y0, x1, y1],
          "text": "Total revenue was 2.4 Cr...",
          "language": "en"
        }
    ]
    """
    extracted_blocks = []
    
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Failed to open PDF {pdf_path}: {e}")
        return extracted_blocks
        
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Get dictionary of block text
        blocks = page.get_text("blocks")
        
        for block in blocks:
            # block[6] represents the block type (0 for text, 1 for image)
            if block[6] == 0:
                text = block[4].strip()
                if not text:
                    continue
                
                # Optional Language Detection Fallback
                try:
                    lang = detect(text)
                except:
                    lang = "unknown"
                    
                block_info = {
                    "page": page_num + 1,
                    "bbox": [block[0], block[1], block[2], block[3]],
                    "text": text,
                    "language": lang
                }
                extracted_blocks.append(block_info)
                
    return extracted_blocks

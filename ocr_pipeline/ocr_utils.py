import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path
import ocrmypdf
import os

def preprocess_image(image):
    """
    Applies preprocessing (deskew, denoise) using OpenCV.
    """
    # Convert PIL Image to OpenCV format
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    # Binarization (Thresholding)
    _, thresh = cv2.threshold(denoised, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    
    # Deskewing
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
    
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
        
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    deskewed = cv2.warpAffine(thresh, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    
    return deskewed

def run_ocr_with_tesseract(pdf_path: str) -> str:
    """
    Converts scanned PDF pages to images, applies preprocessing,
    and runs Tesseract OCR.
    """
    try:
        images = convert_from_path(pdf_path)
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return ""
        
    combined_text = ""
    for i, image in enumerate(images):
        processed_img = preprocess_image(image)
        # Run Tesseract on processed block
        text = pytesseract.image_to_string(processed_img, lang='eng')
        combined_text += f"\n--- Page {i + 1} ---\n"
        combined_text += text
        
    return combined_text

def ocr_with_ocrmypdf(pdf_path: str, output_path: str) -> bool:
    """
    Runs ocrmypdf to deskew and embed OCR layer in-place,
    outputting a searchable PDF.
    """
    try:
        ocrmypdf.ocr(pdf_path, output_path, deskew=True, force_ocr=True)
        return True
    except Exception as e:
        print(f"OCRmyPDF failed: {e}")
        return False

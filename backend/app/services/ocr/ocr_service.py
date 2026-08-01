import os
from PIL import Image
from pypdf import PdfReader
import easyocr

# Initialize EasyOCR reader lazily (English language)
_ocr_reader = None

def get_ocr_reader():
    global _ocr_reader
    if _ocr_reader is None:
        # GPU=False ensures stability if CUDA isn't configured
        _ocr_reader = easyocr.Reader(['en'], gpu=False)
    return _ocr_reader

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts raw text directly from searchable PDF files."""
    extracted_text = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
    except Exception as e:
        print(f"Error reading PDF with PyPDF: {e}")
    return extracted_text.strip()

def extract_text_from_image(image_path: str) -> str:
    """Extracts text from scanned medical images/lab reports using EasyOCR."""
    try:
        reader = get_ocr_reader()
        # EasyOCR extracts detailed text blocks
        results = reader.readtext(image_path, detail=0)
        return "\n".join(results)
    except Exception as e:
        print(f"Error executing EasyOCR: {e}")
        return ""

def process_medical_report(file_path: str) -> str:
    """
    Main entry point for medical report ingestion.
    Supports both PDF and Image formats (PNG, JPG, JPEG).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
        # Fallback to OCR if PDF contains scanned image rather than text
        if not text:
            print("PDF has no embedded text. Running fallback OCR...")
            text = extract_text_from_image(file_path)
    elif ext in [".png", ".jpg", ".jpeg", ".tiff"]:
        text = extract_text_from_image(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
        
    return text.strip()
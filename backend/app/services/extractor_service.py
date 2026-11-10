import os
from pathlib import Path
from typing import Dict, Any, Tuple
import fitz # PyMuPDF
import docx # python-docx
from PIL import Image

def extract_text_from_pdf(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """Extract text and metadata from PDF using PyMuPDF (fitz)."""
    text_content = []
    metadata = {}
    doc = fitz.open(file_path)
    metadata["page_count"] = len(doc)
    metadata["format"] = "PDF"

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_text = page.get_text("text")
        if page_text.strip():
            text_content.append(f"--- Page {page_num + 1} ---\n{page_text.strip()}")

    doc.close()
    full_text = "\n\n".join(text_content)
    return full_text, metadata

def extract_text_from_docx(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """Extract text from Microsoft Word .docx file."""
    doc = docx.Document(file_path)
    paragraphs = []
    
    for p in doc.paragraphs:
        if p.text.strip():
            paragraphs.append(p.text.strip())

    # Also extract text from tables
    for table in doc.tables:
        for row in table.rows:
            row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_text:
                paragraphs.append(" | ".join(row_text))

    metadata = {
        "paragraph_count": len(doc.paragraphs),
        "table_count": len(doc.tables),
        "format": "DOCX"
    }
    return "\n\n".join(paragraphs), metadata

def extract_text_from_image(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """Extract text from image using pytesseract OCR with safe fallback."""
    text = ""
    metadata = {"format": "IMAGE"}
    try:
        import pytesseract
        img = Image.open(file_path)
        metadata["width"] = img.width
        metadata["height"] = img.height
        metadata["mode"] = img.mode
        text = pytesseract.image_to_string(img)
    except Exception as e:
        # OCR might not have tesseract binary in PATH on some Windows environments
        metadata["ocr_note"] = f"OCR engine fallback: {str(e)}"
        text = ""
    return text.strip(), metadata

def extract_content(file_path: str, content_type: str) -> Tuple[str, Dict[str, Any]]:
    """Master extraction dispatcher."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = path.suffix.lower()
    if ext == ".pdf" or content_type == "PDF":
        return extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"] or content_type == "DOCX":
        return extract_text_from_docx(file_path)
    elif ext in [".png", ".jpg", ".jpeg", ".webp"] or content_type == "IMAGE":
        return extract_text_from_image(file_path)
    elif ext in [".txt", ".md", ".json"]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return content, {"format": "TEXT"}
    else:
        # Fallback reading
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            return content, {"format": "TEXT_FALLBACK"}
        except Exception:
            return "", {"format": "UNKNOWN"}


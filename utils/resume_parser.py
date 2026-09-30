import os
import re
from pypdf import PdfReader
import docx

def parse_resume(file_path):
    text = ""
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == '.pdf':
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        elif ext == '.docx':
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
            
        return {
            "text": text,
            "success": True
        }
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Resume Parsing Error: {str(e)}")
        return {
            "success": False,
            "error": "The document format is corrupted or unsupported."
        }

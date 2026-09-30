import os
from werkzeug.utils import secure_filename
from utils.resume_parser import parse_resume
from services.gemini_service import generate_ai_response, GeminiAPIError
from services.ats_service import calculate_ats_score
import json
import logging

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_recommendations(target_role):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    portals_path = os.path.join(base_dir, 'data', 'job_portals.json')
    certs_path = os.path.join(base_dir, 'data', 'certifications.json')
    
    portals = []
    certs = []
    
    if os.path.exists(portals_path):
        with open(portals_path, 'r', encoding='utf-8') as f:
            for p in json.load(f):
                if not target_role or "All" in p.get('roles', []) or any(r.lower() in target_role.lower() for r in p.get('roles', [])):
                    portals.append(p)
                    
    if os.path.exists(certs_path):
        with open(certs_path, 'r', encoding='utf-8') as f:
            for c in json.load(f):
                if not target_role or "All" in c.get('roles', []) or any(r.lower() in target_role.lower() for r in c.get('roles', [])):
                    certs.append(c)
                    
    return portals, certs

def process_resume(file, target_role, upload_folder):
    if not file or file.filename == '':
        return None, "No file selected."
        
    if not allowed_file(file.filename):
        return None, "Only PDF and DOCX files are allowed."
        
    # Check file size by seeking to end
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0, 0)
    
    if file_length > MAX_FILE_SIZE:
        return None, "File size exceeds the 5MB limit."
        
    filename = secure_filename(file.filename)
    filepath = os.path.join(upload_folder, filename)
    
    try:
        file.save(filepath)
        
        # Parse document text
        parsed_data = parse_resume(filepath)
        if not parsed_data['success']:
            return None, f"Failed to parse document: {parsed_data.get('error')}"
            
        resume_text = parsed_data['text']
        
        # Use Gemini to extract structured info and analyze for qualitative feedback
        prompt = f"""
        Act as an expert Resume Analyzer.
        Target Job Role: {target_role if target_role else 'Not specified'}
        
        Resume Text:
        {resume_text}
        
        Instructions:
        Provide structured extraction and feedback. Return ONLY a valid JSON object with the exact following structure. Do not use markdown blocks:
        
        {{
          "extracted_info": {{
            "name": "Applicant Name",
            "email": "Email",
            "phone": "Phone",
            "education": ["Edu 1"],
            "skills": ["Skill 1", "Skill 2"],
            "projects": ["Proj 1"],
            "experience": ["Exp 1"],
            "certifications": ["Cert 1"],
            "achievements": ["Ach 1"]
          }},
          "feedback": "Overall summary of the resume.",
          "areas_for_improvement": ["Improvement 1"],
          "strengths": ["Strength 1"]
        }}
        """
        
        response_text = generate_ai_response(prompt)
        
        # Clean the response text in case the model added markdown blocks
        clean_text = response_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
            
        clean_text = clean_text.strip()
        
        result_data = json.loads(clean_text)
        
        # Calculate ATS score using the deterministic Python algorithm
        ats_results = calculate_ats_score(resume_text, result_data.get("extracted_info", {}), target_role)
        result_data["deterministic_ats"] = ats_results
        
        # Static recommendations (No Gemini hallucination)
        portals, certs = get_recommendations(target_role)
        result_data["job_portals"] = portals
        result_data["certifications"] = certs
        
        return result_data, None
        
    except GeminiAPIError as e:
        return None, str(e)
    except json.JSONDecodeError as e:
        logger.error(f"JSON Parsing Error in Resume Analyzer: {str(e)} - Response: {clean_text}")
        return None, "Failed to parse AI response. Ensure your resume contains readable text."
    except Exception as e:
        logger.error(f"Unexpected error parsing resume: {str(e)}")
        return None, "An unexpected error occurred while analyzing the resume."
    finally:
        # Clean up temporary file
        if os.path.exists(filepath):
            os.remove(filepath)

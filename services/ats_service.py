import json
import os
import re
from typing import Dict, Any

def get_role_data(target_role: str):
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'career_roles.json')
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            roles = json.load(f)
            
        if not target_role:
            return {"required_skills": [], "preferred_skills": []}
            
        # Try exact match, then loose matching
        if target_role in roles:
            return roles[target_role]
            
        for role_name, data in roles.items():
            if role_name.lower() in target_role.lower() or target_role.lower() in role_name.lower():
                return data
                
        # Fallback if no matching role
        return {
            "required_skills": [],
            "preferred_skills": []
        }
    except Exception:
        return {
            "required_skills": [],
            "preferred_skills": []
        }

def calculate_ats_score(resume_text: str, extracted_info: Dict[str, Any], target_role: str) -> Dict[str, Any]:
    role_data = get_role_data(target_role)
    
    resume_text_lower = resume_text.lower()
    extracted_skills_lower = [s.lower() for s in extracted_info.get("skills", [])]
    
    # Analyze sections
    common_sections = ["education", "experience", "projects", "skills", "certifications", "achievements", "summary", "objective"]
    detected_sections = []
    for section in common_sections:
        if re.search(r'\b' + section + r'\b', resume_text_lower):
            detected_sections.append(section.capitalize())
            
    # Skill matching
    required = role_data.get("required_skills", [])
    preferred = role_data.get("preferred_skills", [])
    
    matching_skills = []
    missing_skills = []
    
    for skill in required:
        if skill.lower() in resume_text_lower or skill.lower() in extracted_skills_lower:
            matching_skills.append(skill)
        else:
            missing_skills.append(skill)
            
    for skill in preferred:
        if skill.lower() in resume_text_lower or skill.lower() in extracted_skills_lower:
            if skill not in matching_skills:
                matching_skills.append(skill)
                
    recommended_skills = [s for s in preferred if s not in matching_skills]
    
    # Calculate score deterministically
    score = 0
    
    # Sections score (max 20)
    section_score = min(len(detected_sections) * 4, 20)
    score += section_score
    
    # Required skills score (max 50)
    if required:
        req_score = (len([s for s in required if s in matching_skills]) / len(required)) * 50
        score += req_score
    else:
        # If no role matches exactly, baseline score
        score += 30
        
    # Preferred skills score (max 30)
    if preferred:
        pref_score = (len([s for s in preferred if s in matching_skills]) / len(preferred)) * 30
        score += pref_score
    else:
        score += 20
        
    return {
        "score": int(score),
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "recommended_skills": recommended_skills,
        "detected_sections": detected_sections,
        "keyword_suggestions": missing_skills + recommended_skills
    }

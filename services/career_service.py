import json
import logging
from services.gemini_service import generate_ai_response, GeminiAPIError

logger = logging.getLogger(__name__)

def generate_career_plan(data):
    name = data.get('name', 'User')
    target_role = data.get('targetRole', 'Tech Professional')
    current_skills = data.get('currentSkills', 'None')
    experience_level = data.get('experienceLevel', 'Fresher')
    preferred_domain = data.get('preferredDomain', 'Any')
    
    prompt = f"""
    Act as an expert AI Career Counselor. Generate a personalized 30-day learning roadmap and career plan.
    
    User Profile:
    - Name: {name}
    - Target Job Role: {target_role}
    - Current Skills: {current_skills}
    - Experience Level: {experience_level}
    - Preferred Domain: {preferred_domain}
    
    Instructions:
    Generate a highly realistic and structured career plan tailored to this profile.
    The response MUST be ONLY a valid JSON object matching exactly this structure, with no markdown formatting, no code blocks, and no extra text outside the JSON:
    
    {{
      "career_summary": "A 2-3 sentence summary of their career path and potential.",
      "existing_skills": ["Skill 1", "Skill 2"],
      "skill_gaps": ["Gap 1", "Gap 2"],
      "priority_skills": ["Priority 1", "Priority 2"],
      "roadmap": [
        {{
          "day": 1,
          "topic": "Topic for the day",
          "description": "Brief description of what to learn.",
          "time": "Estimated hours (e.g., '2 hours')",
          "task": "A practical task to apply the knowledge.",
          "resources": ["Resource 1", "Resource 2"]
        }}
      ],
      "resources": ["General Resource 1", "General Resource 2"],
      "projects": ["Project 1", "Project 2"],
      "interview_topics": ["Topic 1", "Topic 2"]
    }}
    
    Ensure the roadmap has logical progression, starting from fundamentals, moving to core tech, then projects, and finally interview prep. Generate at least 5-7 meaningful days in the roadmap, ensuring day numbers are between 1 and 30.
    """
    
    try:
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
        
        try:
            plan_data = json.loads(clean_text)
            return plan_data, None
        except json.JSONDecodeError as e:
            logger.error(f"JSON Parsing Error: {str(e)} - Response Text: {response_text}")
            return None, "Failed to parse AI response. The service returned invalid data formatting. Please try again."
            
    except GeminiAPIError as e:
        return None, str(e)
    except Exception as e:
        logger.error(f"Unexpected error in career_service: {str(e)}")
        return None, "An unexpected error occurred. Please try again."

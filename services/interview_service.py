import json
import os
import logging
from services.gemini_service import generate_ai_response, GeminiAPIError
from datetime import datetime

logger = logging.getLogger(__name__)

def get_history_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'interview_history.json')

def get_interview_history():
    path = get_history_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_interview_result(result_data):
    path = get_history_path()
    history = get_interview_history()
    
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "target_role": result_data.get("target_role", "Unknown"),
        "interview_type": result_data.get("interview_type", "Unknown"),
        "difficulty": result_data.get("difficulty", "Unknown"),
        "total_questions": result_data.get("total_questions", 0),
        "score": result_data.get("score", 0),
        "percentage": result_data.get("percentage", 0),
        "weak_topics": result_data.get("weak_topics", [])
    }
    
    history.insert(0, entry) # Prepend newest
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(history[:50], f, indent=2) # Keep last 50

def generate_mcq_test(data):
    role = data.get('role', 'Software Engineer')
    type_ = data.get('type', 'Technical')
    difficulty = data.get('difficulty', 'Intermediate')
    num_questions = int(data.get('num_questions', 5))
    resume_context = data.get('resume_context', '')
    weak_topics_focus = data.get('weak_topics_focus', '')
    
    prompt = f"""
    Act as an expert technical interviewer and test creator.
    Generate a multiple-choice question (MCQ) test for interview preparation.
    
    Target Role: {role}
    Interview Type: {type_}
    Difficulty: {difficulty}
    Number of Questions: {num_questions}
    """
    
    if weak_topics_focus:
        prompt += f"\nFocus heavily on these weak topics: {weak_topics_focus}\n"
        
    if resume_context:
        prompt += f"\nResume Context to base questions on (do not invent experiences not in here):\n{resume_context}\n"
        
    prompt += """
    Difficulty Guidelines:
    - Beginner: Basic definitions, fundamental concepts, simple examples.
    - Intermediate: Application-based, concept comparison, small code snippets, practical scenarios.
    - Advanced: Scenario-based, debugging, architecture concepts, advanced reasoning.

    Output Requirements:
    - Generate EXACTLY the requested number of questions.
    - Each question MUST have exactly 4 options prefixed with 'A. ', 'B. ', 'C. ', 'D. '.
    - 'correct_answer' must be just the letter ('A', 'B', 'C', or 'D').
    - Do NOT repeat questions.
    - Do NOT create ambiguous questions.
    
    Return ONLY a valid JSON object in the exact following format, with no markdown code blocks:
    
    {
      "questions": [
        {
          "question": "What is...?",
          "options": [
            "A. Option 1",
            "B. Option 2",
            "C. Option 3",
            "D. Option 4"
          ],
          "correct_answer": "B",
          "explanation": "Because...",
          "topic": "Topic Name",
          "difficulty": "Intermediate"
        }
      ]
    }
    """
    
    try:
        response_text = generate_ai_response(prompt)
        
        # Clean markdown
        clean_text = response_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
            
        clean_text = clean_text.strip()
        
        quiz_data = json.loads(clean_text)
        
        if "questions" not in quiz_data or len(quiz_data["questions"]) == 0:
            return None, "The AI returned an empty question set. Please try again."
            
        # Basic validation
        for q in quiz_data["questions"]:
            if len(q.get("options", [])) != 4:
                return None, "Invalid questions generated (missing options). Please try again."
            if q.get("correct_answer") not in ["A", "B", "C", "D"]:
                # Attempt to fix it if the AI returned "A. Option 1" as the answer
                ans = q.get("correct_answer", "")
                if ans.startswith("A"): q["correct_answer"] = "A"
                elif ans.startswith("B"): q["correct_answer"] = "B"
                elif ans.startswith("C"): q["correct_answer"] = "C"
                elif ans.startswith("D"): q["correct_answer"] = "D"
                else:
                    q["correct_answer"] = "A" # Fallback to avoid breaking
                    
        return quiz_data, None
        
    except GeminiAPIError as e:
        return None, str(e)
    except json.JSONDecodeError as e:
        logger.error(f"JSON Parse Error in MCQ: {str(e)} - Output: {response_text}")
        return None, "Unable to generate the interview due to formatting issues. Please try again."
    except Exception as e:
        logger.error(f"Unexpected error in interview gen: {str(e)}")
        return None, "Unable to generate the interview. Please try again."

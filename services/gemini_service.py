import os
import requests
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CodeCraft API Configuration
CODECRAFT_BASE_URL = "https://codecraftapi.com/v1"
CODECRAFT_MODEL = "gemini-3.1-pro"

class GeminiAPIError(Exception):
    pass

def generate_ai_response(prompt):
    """Generate AI response using the CodeCraft API (OpenAI-compatible endpoint)."""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here" or api_key.strip() == "":
            raise GeminiAPIError("Gemini API key is not configured.")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": CODECRAFT_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        }

        response = requests.post(
            f"{CODECRAFT_BASE_URL}/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )

        if response.status_code == 401 or response.status_code == 403:
            logger.error(f"Auth Error: {response.status_code} - {response.text}")
            raise GeminiAPIError("Gemini API authentication failed. Please verify your API key.")

        if response.status_code == 429:
            logger.error(f"Quota Error: {response.text}")
            raise GeminiAPIError("AI service quota exceeded. Please try again later.")

        if response.status_code == 503:
            logger.error(f"Service Unavailable: {response.text}")
            raise GeminiAPIError("AI service is temporarily unavailable. Please try again.")

        if response.status_code != 200:
            logger.error(f"API Error: {response.status_code} - {response.text}")
            raise GeminiAPIError("Network error occurred while contacting AI service. Please try again.")

        result = response.json()
        
        if "choices" not in result or not result["choices"]:
            raise GeminiAPIError("Received empty response from AI service.")

        content = result["choices"][0]["message"]["content"]
        
        if not content or content.strip() == "":
            raise GeminiAPIError("Received empty response from AI service.")

        return content

    except GeminiAPIError:
        raise
    except requests.exceptions.Timeout:
        logger.error("Request timed out while contacting AI service.")
        raise GeminiAPIError("AI service request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        logger.error("Connection error while contacting AI service.")
        raise GeminiAPIError("Network error occurred while contacting AI service. Please try again.")
    except Exception as e:
        logger.error(f"Unexpected Error in generate_ai_response: {str(e)}")
        raise GeminiAPIError("An unexpected error occurred while generating the AI response. Please try again.")

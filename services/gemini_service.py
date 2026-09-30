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
    """Custom exception for CodeCraft/Gemini API errors."""
    pass


def generate_ai_response(prompt):
    """Generate an AI response using the CodeCraft OpenAI-compatible API."""

    try:
        # Get CodeCraft API key from environment
        api_key = os.getenv("CODECRAFT_API_KEY")

        # Safe diagnostic - never print the actual API key
        logger.info(
            f"CodeCraft API key configured: {bool(api_key)}"
        )

        # Validate API key
        if (
            not api_key
            or api_key.strip() == ""
            or api_key == "your_codecraft_api_key_here"
        ):
            raise GeminiAPIError(
                "CodeCraft API key is not configured."
            )

        # Request headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Request body
        data = {
            "model": CODECRAFT_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        }

        # Send request to CodeCraft
        response = requests.post(
            f"{CODECRAFT_BASE_URL}/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )

        # 401 - Authentication failure
        if response.status_code == 401:
            logger.error(
                f"CodeCraft Authentication Error: "
                f"{response.status_code} - {response.text}"
            )

            raise GeminiAPIError(
                "CodeCraft API authentication failed. "
                "Please verify your API key."
            )

        # 403 - Permission/access problem
        if response.status_code == 403:
            logger.error(
                f"CodeCraft Permission Error: "
                f"{response.status_code} - {response.text}"
            )

            raise GeminiAPIError(
                "CodeCraft API access was denied. "
                "Please check your API key permissions."
            )

        # 429 - Rate limit/quota
        if response.status_code == 429:
            logger.error(
                f"CodeCraft Quota Error: {response.text}"
            )

            raise GeminiAPIError(
                "AI service quota exceeded. "
                "Please try again later."
            )

        # 503 - Service unavailable
        if response.status_code == 503:
            logger.error(
                f"CodeCraft Service Unavailable: "
                f"{response.text}"
            )

            raise GeminiAPIError(
                "AI service is temporarily unavailable. "
                "Please try again."
            )

        # 404 - Model/endpoint problem
        if response.status_code == 404:
            logger.error(
                f"CodeCraft Model/Endpoint Error: "
                f"{response.text}"
            )

            raise GeminiAPIError(
                "The requested AI model or endpoint "
                "was not found."
            )

        # Other HTTP errors
        if response.status_code != 200:
            logger.error(
                f"CodeCraft API Error: "
                f"{response.status_code} - {response.text}"
            )

            raise GeminiAPIError(
                "Network error occurred while contacting "
                "the AI service. Please try again."
            )

        # Parse JSON response
        try:
            result = response.json()
        except ValueError:
            logger.error(
                f"Invalid JSON response: {response.text}"
            )

            raise GeminiAPIError(
                "Received an invalid response from the AI service."
            )

        # Validate choices
        if (
            "choices" not in result
            or not result["choices"]
        ):
            logger.error(
                f"Empty AI response: {result}"
            )

            raise GeminiAPIError(
                "Received empty response from AI service."
            )

        # Extract generated content
        message = result["choices"][0].get("message", {})
        content = message.get("content", "")

        # Validate content
        if not content or not content.strip():
            raise GeminiAPIError(
                "Received empty response from AI service."
            )

        return content.strip()

    # Re-raise our custom errors
    except GeminiAPIError:
        raise

    # Request timeout
    except requests.exceptions.Timeout:
        logger.error(
            "Request timed out while contacting CodeCraft."
        )

        raise GeminiAPIError(
            "AI service request timed out. Please try again."
        )

    # Connection error
    except requests.exceptions.ConnectionError:
        logger.error(
            "Connection error while contacting CodeCraft."
        )

        raise GeminiAPIError(
            "Network error occurred while contacting "
            "AI service. Please try again."
        )

    # Any unexpected error
    except Exception as e:
        logger.exception(
            f"Unexpected error in generate_ai_response: {str(e)}"
        )

        raise GeminiAPIError(
            "An unexpected error occurred while generating "
            "the AI response. Please try again."
        )

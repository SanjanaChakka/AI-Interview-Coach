# interview_engine.py
# -----------------------------------------------------------
# This file manages the AI interview logic:
# - Connecting to the Gemini API
# - Generating the next question
# - Keeping track of questions asked so far
# -----------------------------------------------------------

from google import genai
from config import GEMINI_API_KEY, LLM_MODEL, TOTAL_QUESTIONS
from prompts import get_question_prompt

# Create ONE reusable client connection to Gemini
client = genai.Client(api_key=GEMINI_API_KEY)


def ask_ai(prompt):
    """
    Sends a prompt (a text instruction) to Gemini and returns its reply as plain text.
    Handles errors gracefully so the app doesn't crash if the API fails.
    """
    try:
        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt,
        )
        return response.text.strip()

    except Exception as e:
        # If the API call fails (bad key, no internet, rate limit, etc.),
        # we return a clear error message instead of crashing the app.
        return f"ERROR: Could not reach AI service. Details: {str(e)}"


def generate_next_question(role, experience, difficulty, previous_questions, question_number):
    """
    Builds the prompt for the next question and asks the AI for it.
    """
    prompt = get_question_prompt(
        role=role,
        experience=experience,
        difficulty=difficulty,
        previous_questions=previous_questions,
        question_number=question_number,
        total_questions=TOTAL_QUESTIONS,
    )

    question = ask_ai(prompt)
    return question
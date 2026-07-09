# config.py
# ---------------------------------------------
# Centralized configuration for the whole app.
# Keeping this separate means if we switch LLM
# providers or models, we only edit ONE file.
# ---------------------------------------------

import os
from dotenv import load_dotenv

load_dotenv()

# Fetch the API key securely — never hardcode this in code
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# The model name is configurable, so switching models
# doesn't require touching logic files
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-flash")

# App-wide constants used across multiple files
ROLES = [
    "Java Developer",
    "Python Developer",
    "Frontend Developer",
    "Full Stack Developer",
    "Data Analyst",
    "Custom Role"
]

EXPERIENCE_LEVELS = ["Fresher", "1-2 Years", "3-5 Years"]

DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]

TOTAL_QUESTIONS = 2

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not found. Please set it in your .env file.")
# evaluator.py
# -----------------------------------------------------------
# This file handles evaluating a candidate's answer using the AI,
# and generating the final interview report at the end.
# -----------------------------------------------------------

import json
from interview_engine import ask_ai
from prompts import get_evaluation_prompt, get_final_report_prompt


def clean_json_response(raw_text):
    """
    Some AI models wrap JSON replies in markdown code fences like:
```json
    { ... }
```
    This function strips those fences so json.loads() can parse it cleanly.
    """
    text = raw_text.strip()

    # Remove opening fence (```json or ```)
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text

    # Remove closing fence
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]

    return text.strip()


def evaluate_answer(role, question, answer):
    """
    Sends the question + answer to the AI and gets back a structured evaluation.
    """
    prompt = get_evaluation_prompt(role, question, answer)
    raw_response = ask_ai(prompt)
    cleaned_response = clean_json_response(raw_response)

    try:
        evaluation = json.loads(cleaned_response)
        return evaluation

    except json.JSONDecodeError:
        return {
            "score": 0,
            "strengths": "N/A",
            "weaknesses": "Could not evaluate this answer due to a formatting error.",
            "ideal_answer": "N/A",
            "suggestions": "Please try answering again.",
        }


def generate_final_report(role, experience, qa_history):
    """
    Sends the full interview transcript to the AI and gets back a final report.
    """
    prompt = get_final_report_prompt(role, experience, qa_history)
    raw_response = ask_ai(prompt)

    # TEMPORARY DEBUG LINES — shows us exactly what Gemini returned.
    # We'll remove these once the issue is fixed.
    print("----- RAW FINAL REPORT RESPONSE -----")
    print(raw_response)
    print("--------------------------------------")

    cleaned_response = clean_json_response(raw_response)

    try:
        report = json.loads(cleaned_response)
        return report

    except json.JSONDecodeError:
        return {
            "overall_score": 0,
            "communication_score": 0,
            "technical_score": 0,
            "problem_solving_score": 0,
            "confidence_score": 0,
            "areas_to_improve": "N/A",
            "recommended_topics": [],
            "final_feedback": "Could not generate the final report due to a formatting error.",
        }
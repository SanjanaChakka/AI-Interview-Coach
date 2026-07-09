# prompts.py
# -----------------------------------------------------------
# This file builds the text messages (prompts) we send to the AI.
# Same idea as before: functions that take simple inputs (role,
# difficulty, etc.) and turn them into a full instruction for the LLM.
# -----------------------------------------------------------


def get_question_prompt(role, experience, difficulty, previous_questions, question_number, total_questions):
    """
    Builds the prompt asking the AI for the NEXT interview question.
    """

    # Turn the list of past questions into readable text,
    # so the AI knows what NOT to repeat.
    if previous_questions:
        previous_text = "\n".join([f"- {q}" for q in previous_questions])
    else:
        previous_text = "None yet — this is the first question."

    # Alternate: odd question numbers = technical, even = behavioral
    question_type = "technical" if question_number % 2 != 0 else "behavioral"

    prompt = f"""
You are an interviewer conducting a mock interview.

Role: {role}
Experience: {experience}
Difficulty: {difficulty}
This is question {question_number} of {total_questions}, focused on being a {question_type} question.

Questions already asked (do not repeat these):
{previous_text}

Return ONLY one clear interview question. No extra text, no preamble.
"""
    return prompt.strip()


def get_evaluation_prompt(role, question, answer):
    """
    Builds the prompt asking the AI to evaluate one answer.
    Asks for the reply in JSON so our code can read it easily.
    """
    prompt = f"""
You are evaluating a candidate's interview answer.

Role: {role}
Question: {question}
Answer: {answer}

Respond ONLY in this JSON format, nothing else:
{{
  "score": <0-10>,
  "strengths": "...",
  "weaknesses": "...",
  "ideal_answer": "...",
  "suggestions": "..."
}}
"""
    return prompt.strip()


def get_final_report_prompt(role, experience, qa_history):
    """
    Builds the prompt asking the AI for the FINAL report,
    based on all questions/answers from the whole interview.
    """
    transcript_parts = []
    for i, entry in enumerate(qa_history, start=1):
        transcript_parts.append(
            f"Q{i}: {entry['question']}\nAnswer: {entry['answer']}\nScore: {entry['evaluation']['score']}/10"
        )
    transcript = "\n".join(transcript_parts)

    prompt = f"""
You are summarizing a candidate's full mock interview performance.

Role: {role}
Experience: {experience}

Transcript:
{transcript}

Respond ONLY in this JSON format, nothing else:
{{
  "overall_score": <0-10>,
  "communication_score": <0-10>,
  "technical_score": <0-10>,
  "problem_solving_score": <0-10>,
  "confidence_score": <0-10>,
  "areas_to_improve": "...",
  "recommended_topics": ["topic1", "topic2", "topic3"],
  "final_feedback": "..."
}}
"""
    return prompt.strip()
# report_generator.py
# -----------------------------------------------------------
# This file converts the final report (a Python dictionary) into
# a downloadable PDF file using the fpdf2 library.
# -----------------------------------------------------------

from fpdf import FPDF
import os


def clean_text(text):
    """
    Removes/replaces characters that the PDF font (Helvetica) can't render,
    and breaks up extremely long unbroken words that fpdf2 can't wrap.
    """
    if not isinstance(text, str):
        text = str(text)

    if not text.strip():
        return "N/A"

    # Replace common problematic Unicode characters with safe equivalents
    replacements = {
        "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-",
        "\u2026": "...",
        "\u2022": "-",
        "\n": " ",   # remove raw newlines (multi_cell handles wrapping itself)
        "\t": " ",
    }
    for bad_char, good_char in replacements.items():
        text = text.replace(bad_char, good_char)

    # Drop any remaining unsupported characters (emojis, etc.) instead of crashing
    text = text.encode("latin-1", "ignore").decode("latin-1")

    # Break up very long unbroken "words" (no spaces) that fpdf2 can't wrap,
    # e.g. long URLs or run-on text. Insert a space every 60 characters.
    words = text.split(" ")
    safe_words = []
    for word in words:
        if len(word) > 60:
            chunks = [word[i:i + 60] for i in range(0, len(word), 60)]
            safe_words.append(" ".join(chunks))
        else:
            safe_words.append(word)
    text = " ".join(safe_words)

    return text.strip() if text.strip() else "N/A"


def safe_multi_cell(pdf, height, text):
    """
    Wraps pdf.multi_cell() in a try/except so that if ANY single line
    still fails to render for an unexpected reason, we skip that line
    instead of crashing the entire PDF generation.
    """
    try:
        pdf.multi_cell(0, height, clean_text(text))
    except Exception:
        pdf.multi_cell(0, height, "[Content could not be displayed]")


def generate_pdf_report(role, experience, difficulty, qa_history, final_report, output_path="reports/interview_report.pdf"):
    """
    Creates a PDF file summarizing the entire interview.
    Returns the file path of the saved PDF.
    """

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ---- Title ----
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, clean_text("AI Interview Coach - Report"), ln=True, align="C")
    pdf.ln(5)

    # ---- Candidate Info ----
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, clean_text(f"Role: {role}"), ln=True)
    pdf.cell(0, 8, clean_text(f"Experience Level: {experience}"), ln=True)
    pdf.cell(0, 8, clean_text(f"Difficulty: {difficulty}"), ln=True)
    pdf.ln(5)

    # ---- Question-by-question breakdown ----
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, clean_text("Interview Transcript & Evaluation"), ln=True)
    pdf.set_font("Helvetica", "", 11)

    for i, entry in enumerate(qa_history, start=1):
        eval_data = entry.get("evaluation", {})

        pdf.set_font("Helvetica", "B", 11)
        safe_multi_cell(pdf, 7, f"Q{i}: {entry.get('question', '')}")

        pdf.set_font("Helvetica", "", 11)
        safe_multi_cell(pdf, 7, f"Answer: {entry.get('answer', '')}")
        safe_multi_cell(pdf, 7, f"Score: {eval_data.get('score', 'N/A')}/10")
        safe_multi_cell(pdf, 7, f"Strengths: {eval_data.get('strengths', '')}")
        safe_multi_cell(pdf, 7, f"Weaknesses: {eval_data.get('weaknesses', '')}")
        safe_multi_cell(pdf, 7, f"Ideal Answer: {eval_data.get('ideal_answer', '')}")
        safe_multi_cell(pdf, 7, f"Suggestions: {eval_data.get('suggestions', '')}")
        pdf.ln(4)

    # ---- Final Report Section ----
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, clean_text("Final Report"), ln=True)
    pdf.set_font("Helvetica", "", 11)

    pdf.cell(0, 8, clean_text(f"Overall Score: {final_report.get('overall_score', 'N/A')}/10"), ln=True)
    pdf.cell(0, 8, clean_text(f"Communication: {final_report.get('communication_score', 'N/A')}/10"), ln=True)
    pdf.cell(0, 8, clean_text(f"Technical Knowledge: {final_report.get('technical_score', 'N/A')}/10"), ln=True)
    pdf.cell(0, 8, clean_text(f"Problem Solving: {final_report.get('problem_solving_score', 'N/A')}/10"), ln=True)
    pdf.cell(0, 8, clean_text(f"Confidence: {final_report.get('confidence_score', 'N/A')}/10"), ln=True)
    pdf.ln(3)

    safe_multi_cell(pdf, 7, f"Areas to Improve: {final_report.get('areas_to_improve', '')}")
    pdf.ln(2)

    topics = ", ".join(final_report.get("recommended_topics", []) or [])
    safe_multi_cell(pdf, 7, f"Recommended Topics: {topics}")
    pdf.ln(2)

    safe_multi_cell(pdf, 7, f"Final Feedback: {final_report.get('final_feedback', '')}")

    # ---- Save the PDF file to disk ----
    pdf.output(output_path)
    return output_path
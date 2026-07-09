# app.py
# -----------------------------------------------------------
# Main Streamlit app. This file controls what the user SEES
# and handles button clicks. All the "thinking" (AI calls,
# scoring, PDF generation) happens in the other files —
# this file just calls those functions and displays results.
# -----------------------------------------------------------

import streamlit as st
from config import ROLES, EXPERIENCE_LEVELS, DIFFICULTY_LEVELS, TOTAL_QUESTIONS
from utils import init_session_state, reset_interview
from interview_engine import generate_next_question
from evaluator import evaluate_answer, generate_final_report
from report_generator import generate_pdf_report

# ---- Page config (must be the first Streamlit command) ----
st.set_page_config(page_title="AI Interview Coach", page_icon="🎯", layout="centered")

# ---- Initialize session state (our "memory" across reruns) ----
init_session_state()


# =============================================================
# PAGE 1: LANDING PAGE
# =============================================================
def show_landing_page():
    st.title("🎯 AI Interview Coach")
    st.write(
        "Practice real interview questions tailored to your role, experience, "
        "and difficulty level — with instant AI-powered feedback after every answer."
    )
    st.markdown("---")

    if st.button("🚀 Start Interview", use_container_width=True):
        st.session_state.page = "setup"
        st.rerun()


# =============================================================
# PAGE 2: SETUP (Role, Experience, Difficulty)
# =============================================================
def show_setup_page():
    st.title("Interview Setup")

    role_choice = st.selectbox("Select your target role:", ROLES)

    custom_role_text = ""
    if role_choice == "Custom Role":
        custom_role_text = st.text_input("Enter your custom role:")

    experience_choice = st.radio("Select your experience level:", EXPERIENCE_LEVELS)

    difficulty_choice = st.select_slider(
        "Select difficulty level:", options=DIFFICULTY_LEVELS
    )

    st.markdown("---")

    if st.button("Begin Interview ➡️", use_container_width=True):
        final_role = custom_role_text if role_choice == "Custom Role" else role_choice

        if role_choice == "Custom Role" and not custom_role_text.strip():
            st.warning("Please enter your custom role before continuing.")
            return

        st.session_state.role = final_role
        st.session_state.experience = experience_choice
        st.session_state.difficulty = difficulty_choice
        st.session_state.page = "interview"
        st.rerun()


# =============================================================
# PAGE 3: INTERVIEW LOOP
# =============================================================
def show_interview_page():
    st.title("🎤 Mock Interview")

    with st.sidebar:
        st.subheader("Session Details")
        st.write(f"**Role:** {st.session_state.role}")
        st.write(f"**Experience:** {st.session_state.experience}")
        st.write(f"**Difficulty:** {st.session_state.difficulty}")
        st.markdown("---")
        progress = st.session_state.question_number / TOTAL_QUESTIONS
        st.progress(progress, text=f"Question {st.session_state.question_number} of {TOTAL_QUESTIONS}")

    if st.session_state.question_number >= TOTAL_QUESTIONS:
        st.session_state.page = "report"
        st.rerun()
        return

    if st.session_state.current_question is None:
        with st.spinner("Generating your next question..."):
            previous_questions = [entry["question"] for entry in st.session_state.qa_history]
            question = generate_next_question(
                role=st.session_state.role,
                experience=st.session_state.experience,
                difficulty=st.session_state.difficulty,
                previous_questions=previous_questions,
                question_number=st.session_state.question_number + 1,
            )
            st.session_state.current_question = question

    st.markdown("### Question")
    st.info(st.session_state.current_question)

    answer = st.text_area("Your answer:", height=150, key=f"answer_{st.session_state.question_number}")

    if st.button("Submit Answer ✅", use_container_width=True):
        if not answer.strip():
            st.warning("Please type an answer before submitting.")
            return

        with st.spinner("Evaluating your answer..."):
            evaluation = evaluate_answer(
                role=st.session_state.role,
                question=st.session_state.current_question,
                answer=answer,
            )

        st.session_state.qa_history.append({
            "question": st.session_state.current_question,
            "answer": answer,
            "evaluation": evaluation,
        })

        st.markdown("### 📊 Evaluation")
        score = evaluation.get("score", 0)

        if score >= 7:
            st.success(f"Score: {score}/10")
        elif score >= 4:
            st.warning(f"Score: {score}/10")
        else:
            st.error(f"Score: {score}/10")

        with st.expander("Strengths"):
            st.write(evaluation.get("strengths", "N/A"))
        with st.expander("Weaknesses"):
            st.write(evaluation.get("weaknesses", "N/A"))
        with st.expander("Ideal Answer"):
            st.write(evaluation.get("ideal_answer", "N/A"))
        with st.expander("Suggestions"):
            st.write(evaluation.get("suggestions", "N/A"))

        st.session_state.question_number += 1
        st.session_state.current_question = None

        if st.button("Continue ➡️", use_container_width=True):
            st.rerun()


# =============================================================
# PAGE 4: FINAL REPORT
# =============================================================
def show_report_page():
    st.title("📋 Final Interview Report")

    if st.session_state.final_report is None:
        with st.spinner("Generating your final report..."):
            st.session_state.final_report = generate_final_report(
                role=st.session_state.role,
                experience=st.session_state.experience,
                qa_history=st.session_state.qa_history,
            )

    report = st.session_state.final_report

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Overall Score", f"{report.get('overall_score', 'N/A')}/10")
        st.metric("Technical Knowledge", f"{report.get('technical_score', 'N/A')}/10")
        st.metric("Confidence", f"{report.get('confidence_score', 'N/A')}/10")
    with col2:
        st.metric("Communication", f"{report.get('communication_score', 'N/A')}/10")
        st.metric("Problem Solving", f"{report.get('problem_solving_score', 'N/A')}/10")

    st.markdown("---")

    st.subheader("Areas to Improve")
    st.write(report.get("areas_to_improve", "N/A"))

    st.subheader("Recommended Topics to Study")
    topics = report.get("recommended_topics", [])
    for topic in topics:
        st.write(f"- {topic}")

    st.subheader("Final Feedback")
    st.write(report.get("final_feedback", "N/A"))

    st.markdown("---")

    with st.expander("📝 View Full Interview Transcript"):
        for i, entry in enumerate(st.session_state.qa_history, start=1):
            st.markdown(f"**Q{i}: {entry['question']}**")
            st.write(f"Your answer: {entry['answer']}")
            st.write(f"Score: {entry['evaluation'].get('score', 'N/A')}/10")
            st.markdown("---")

    if st.button("📄 Generate & Download PDF Report", use_container_width=True):
        with st.spinner("Creating your PDF report..."):
            pdf_path = generate_pdf_report(
                role=st.session_state.role,
                experience=st.session_state.experience,
                difficulty=st.session_state.difficulty,
                qa_history=st.session_state.qa_history,
                final_report=report,
            )

        with open(pdf_path, "rb") as f:
            st.download_button(
                label="⬇️ Click to Download PDF",
                data=f,
                file_name="AI_Interview_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    if st.button("🔄 Start New Interview", use_container_width=True):
        reset_interview()
        st.rerun()


# =============================================================
# MAIN ROUTER: decides which page function to run
# =============================================================
if st.session_state.page == "landing":
    show_landing_page()
elif st.session_state.page == "setup":
    show_setup_page()
elif st.session_state.page == "interview":
    show_interview_page()
elif st.session_state.page == "report":
    show_report_page()
# utils.py
# -----------------------------------------------------------
# Small reusable helper functions used across the app.
# Mainly for managing Streamlit's "session state" —
# the memory that persists while a user is using the app.
# -----------------------------------------------------------

import streamlit as st


def init_session_state():
    """
    Sets up all the variables we need to track during an interview session.
    Streamlit reruns the entire script on every user interaction, so
    session_state is how we "remember" things between those reruns
    (similar to component state in React, but simpler).
    """
    defaults = {
        "page": "landing",          # which screen we're on
        "role": None,
        "custom_role": "",
        "experience": None,
        "difficulty": None,
        "question_number": 0,
        "current_question": None,
        "qa_history": [],           # list of {question, answer, evaluation}
        "interview_complete": False,
        "final_report": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_interview():
    """
    Resets everything back to the start, so the user can begin a new interview.
    """
    st.session_state.page = "landing"
    st.session_state.role = None
    st.session_state.custom_role = ""
    st.session_state.experience = None
    st.session_state.difficulty = None
    st.session_state.question_number = 0
    st.session_state.current_question = None
    st.session_state.qa_history = []
    st.session_state.interview_complete = False
    st.session_state.final_report = None
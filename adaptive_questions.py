# adaptive_questions.py
import streamlit as st

def adaptive_question_block():
    """
    Show extra fields if certain conditions are met (e.g. project-based role).
    """
    job_reason = st.session_state.get("job_reason", [])
    if isinstance(job_reason, list) and "Project-based" in job_reason:
        st.write("Since this is a project-based role, please clarify project scope/duration:")
        scope = st.text_area("Project Scope / Duration", "")
        st.session_state["project_scope"] = scope

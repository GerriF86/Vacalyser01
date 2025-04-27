# progress_checklist.py
import streamlit as st

def progress_checklist_page():
    st.header("✅ Completion Checklist")
    st.markdown("""
    Below is a summary of required fields for a well-defined job spec. 
    Check off everything that's completed.
    """)
    # Updated required fields matching session keys
    required_fields = [
        "job_title", "company_name", "city", "salary_range"
    ]
    missing = []
    for f in required_fields:
        val = st.session_state.get(f, "")
        if not val:
            missing.append(f)
    if missing:
        st.warning(f"The following fields are still missing: {', '.join(missing)}")
    else:
        st.success("All key fields are filled in. Great job!")
    st.markdown("You can go back to relevant sections to fill them out at any time.")

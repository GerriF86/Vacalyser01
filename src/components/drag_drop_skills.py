#drag_drop_skills.py

import streamlit as st

def drag_drop_skills_component():
    """
    Simple demonstration of collecting must-have vs. nice-to-have skills in separate text areas.
    """
    st.write("### Must-Have Skills")
    must_have_raw = st.text_area(
        "Enter must-have skills (one per line):",
        value=st.session_state.get("must_have_skills", "")
    )
    st.write("### Nice-to-Have Skills")
    nice_have_raw = st.text_area(
        "Enter nice-to-have skills (one per line):",
        value=st.session_state.get("nice_to_have_skills", "")
    )

    # Convert input to lists
    must_have_list = [skill.strip() for skill in must_have_raw.split("\n") if skill.strip()]
    nice_have_list = [skill.strip() for skill in nice_have_raw.split("\n") if skill.strip()]

    # Store them
    st.session_state["must_have_skills"] = "\n".join(must_have_list)
    st.session_state["nice_to_have_skills"] = "\n".join(nice_have_list)

#dynamic_forms.py

import streamlit as st

def text_input_with_session(label: str, key: str, placeholder: str = ""):
    """
    Helper that updates st.session_state.
    """
    st.session_state[key] = st.text_input(
        label,
        value=st.session_state.get(key, ""),
        placeholder=placeholder
    )

def text_area_with_session(label: str, key: str, placeholder: str = "", height=100):
    """
    Helper for text_area that updates session_state.
    """
    st.session_state[key] = st.text_area(
        label,
        value=st.session_state.get(key, ""),
        placeholder=placeholder,
        height=height
    )

def confirm_section_summary(section_key: str):
    """
    Displays a quick summary for a single field.
    """
    current_val = st.session_state.get(section_key, "")
    if current_val.strip():
        st.write(f"**{section_key}:** {current_val}")
    else:
        st.write(f"**{section_key}:** Not provided")

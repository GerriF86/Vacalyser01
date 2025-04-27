import streamlit as st

def apply_base_styling():
    """
    Inject custom CSS styling for a futuristic look:
    - Gradient background
    - Custom button styles
    - Hide default Streamlit branding
    """
    st.markdown("""
    <style>
    /* Gradient background for main app */
    .main, body {
        background: linear-gradient(to bottom right, #0f0c29, #302b63, #24243e);
        color: #FFFFFF;
    }
    /* Style buttons with custom colors */
    div.stButton > button {
        background: linear-gradient(to right, #6a11cb, #2575fc);
        color: #FFFFFF;
        border: none;
        border-radius: 4px;
        padding: 0.5em 1em;
    }
    div.stButton > button:hover {
        opacity: 0.9;
    }
    /* Hide Streamlit header and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

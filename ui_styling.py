import streamlit as st

def apply_base_styling():
    """
    Defines a dark CSS theme for the entire app, removing leftover white backgrounds.
    """
    st.markdown(
        """
        <style>
        body, .block-container, .main {
            background-color: #353536 !important;
            color: #b1b3b3 !important;
            margin: 0; 
            padding: 0;
            font-family: 'Comfortaa', sans-serif;
        }
        h1, h2, h3, h4 {
            color: #ffffff !important;
        }
        .stButton > button, .stSidebar .stButton > button {
            background-color: #2e3232 !important;
            color: #ffffff !important;
            border: none;
            border-radius: 6px;
            font-size: 1rem;
        }
        /* Overriding the file uploader container */
        .stFileUploader, .stFileUploader > label {
            background-color: transparent !important;
            color: #b1b3b3 !important;
        }
        div[data-testid="stFileUploadDropzone"] {
            background-color: #2e3232 !important;
            border: none !important;
            min-height: 40px !important;
        }
        /* Overriding ephemeral classes if needed */
        .css-1c9lpua, .css-1opk6do, .css-1cjp0ke, .css-19ih76x,
        .uploadedFile, .css-1v0mbdj, .css-18e3th9, .css-1r5n7tp {
            background-color: #2e3232 !important;
            border: none !important;
            box-shadow: none !important;
        }
        label, .stMarkdown p, .stCheckbox, .stRadio, .stSelectbox {
            color: #cccccc !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

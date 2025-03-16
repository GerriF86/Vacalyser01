import streamlit as st
from navigation import PAGE_FUNCTIONS
from ui_elements import show_progress_bar
from functions import get_from_session_state
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env
def main():
    # 1) Set Streamlit’s page title + layout (wide).
    st.set_page_config(page_title="Vacalyser", layout="wide")

    # 2) If "current_section" not in session, initialize to 0.
    if "current_section" not in st.session_state:
        st.session_state["current_section"] = 0

    # 3) Read the "current_section" from session state.
    current_section = get_from_session_state("current_section", 0)

    # 4) The total number of pages in the wizard, from PAGE_FUNCTIONS.
    total_pages = len(PAGE_FUNCTIONS)

    # 5) Show a progress bar, e.g. at top, to indicate user’s progress.
    show_progress_bar(current_section, total_pages)

    # 6) Display the correct page by indexing into PAGE_FUNCTIONS.
    PAGE_FUNCTIONS[current_section]()

if __name__ == "__main__":
    # 7) Standard Pythonic entry point for the script. 
    main()

import streamlit as st
from src.utils.ui import apply_base_styling

st.set_page_config(page_title="About Vacalyser", layout="wide")
apply_base_styling()

st.title("About Vacalyser")
st.write("""
Vacalyser is a **futuristic recruitment analysis wizard** that streamlines the job creation and hiring process.
It leverages advanced AI models to analyze job descriptions, suggest improvements, and generate recruitment content automatically.
Developed to assist HR teams and recruiters, Vacalyser ensures that job ads are comprehensive and appealing, 
and helps identify optimal candidate sourcing strategies.
""")
st.write("""
**Key Features:**
- Intelligent parsing of job descriptions to pre-fill structured job details.
- AI-powered suggestions for tasks, skills, and benefits to include.
- Automated generation of job advertisements, interview preparation guides, and contract drafts.
- Insights on sourcing channels and search strategies to find the best candidates.
""")
st.write("Vacalyser brings efficiency and quality together, reducing time-to-hire and improving the hiring experience for all parties.")

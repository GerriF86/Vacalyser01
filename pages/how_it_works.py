import streamlit as st
from src.utils.ui import apply_base_styling

st.set_page_config(page_title="How It Works - Vacalyser", layout="wide")
apply_base_styling()

st.title("How Vacalyser Works")
st.write("""
Vacalyser guides you through a **step-by-step wizard** to build a job profile and recruitment plan:
""")
st.markdown("""
1. **Input Job Details:** Start by entering the job title, or uploading an existing job ad, or even a company page URL. Vacalyser will analyze any provided text and auto-fill relevant fields for you.
2. **Structured Role Definition:** Proceed through sections for company info, role description, tasks, skills, and benefits. Each section is pre-populated where possible, and you can edit or add details.
3. **AI-Powered Suggestions:** At each step, you can generate AI suggestions. Vacalyser compares outputs from multiple AI models (local and OpenAI) side-by-side for tasks, skills, and benefits, allowing you to quickly add the ones you like with a single click.
4. **Recruitment Process:** Define the hiring process details such as interview rounds, timelines, and contacts.
5. **Final Review & Outputs:** Review a summary of all information. Vacalyser can then create a polished job advertisement, prepare interview question guides, and even draft an offer letter or contract – all downloadable for your convenience.
6. **Sourcing Strategy:** Vacalyser provides boolean search strings and suggests niche channels to find candidates, tailoring the sourcing strategy to your role and target group.
""")
st.write("""
Throughout the process, Vacalyser uses an **intelligent dynamic flow**, adjusting suggestions based on what you've already provided. 
The result is a comprehensive job profile and a ready-to-go toolkit for hiring – all created efficiently with the help of AI.
""")

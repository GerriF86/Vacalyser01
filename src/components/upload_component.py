# upload_component.py
 
import streamlit as st
from src.utils.extraction import extract_text_from_pdf
import docx

def file_uploader_component():
    """
    Allows user to upload a PDF, DOCX, 
    or TXT file; automatically extracts text.
    Returns the extracted text or "" if no file is uploaded.
    """
    uploaded_file = st.file_uploader("Upload your job ad:", type=["pdf", "docx", "txt"])
    if uploaded_file:
        file_type = uploaded_file.name.split(".")[-1].lower()
        if file_type == "pdf":
            return extract_text_from_pdf(uploaded_file)
        elif file_type == "docx":
            document = docx.Document(uploaded_file)
            return "\n".join([para.text for para in document.paragraphs])
        elif file_type == "txt":
            return uploaded_file.read().decode("utf-8", errors="ignore")
    return ""

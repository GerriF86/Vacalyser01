#extraction.py

import os
import re
import fitz  # PyMuPDF for PDF extraction
import docx
import json
from src.utils.llm_service import LLMService

def clean_text(text: str) -> str:
    """Basic cleaning of text: remove extra whitespace."""
    return re.sub(r'\s+', ' ', text).strip()

def extract_structured_info(raw_text: str, keys: list):
    """
    Use an LLM to extract structured information from raw job ad text.
    Returns a dictionary with the given keys and extracted values.
    """
    # Initialize LLM (using OpenAI for extraction by default)
    llm = LLMService(provider="openai", openai_api_key=os.getenv("OPENAI_API_KEY", ""), 
                     openai_org=os.getenv("OPENAI_ORGANIZATION", ""), openai_model="gpt-3.5-turbo")
    keys_list = ', '.join(keys)
    prompt = (f"Extract the following fields from the job description text below. Return only JSON:\n"
              f"Fields: {keys_list}\n\nJob Description:\n{raw_text}\n\nJSON Output:")
    response = llm.complete(prompt, max_tokens=512)
    try:
        structured_data = json.loads(response)
    except json.JSONDecodeError:
        structured_data = {}
    return structured_data

def extract_text_from_pdf(uploaded_pdf) -> str:
    """Read text from an uploaded PDF file."""
    pdf_data = uploaded_pdf.read()
    try:
        doc = fitz.open(stream=pdf_data, filetype="pdf")
    except Exception:
        return ""
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(uploaded_docx) -> str:
    """Read text from an uploaded DOCX file."""
    document = docx.Document(uploaded_docx)
    full_text = [para.text for para in document.paragraphs]
    return "\n".join(full_text)

def extract_text_from_txt(uploaded_txt) -> str:
    """Read text from an uploaded TXT file."""
    content = uploaded_txt.read()
    try:
        return content.decode("utf-8", errors="ignore")
    except:
        return str(content)

def extract_uploaded_file(uploaded_file):
    """Extract raw text content from an uploaded job ad file (PDF, DOCX, or TXT)."""
    filename = uploaded_file.name.lower()
    if filename.endswith(".pdf"):
        raw_text = extract_text_from_pdf(uploaded_file)
    elif filename.endswith(".docx"):
        raw_text = extract_text_from_docx(uploaded_file)
    elif filename.endswith(".txt"):
        raw_text = extract_text_from_txt(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: {uploaded_file.name}")
    return clean_text(raw_text)

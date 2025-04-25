import fitz  # PyMuPDF
import docx
from .preprocessing import clean_text
import json
from src.services.llm_service import LLMService

def extract_structured_info(raw_text, keys):
    llm_service = LLMService()
    
    prompt = (
        f"Extract structured information from the job ad below. Return JSON only with keys: {keys}.\n\n"
        f"Job Ad Text:\n{raw_text}\n\n"
        f"Output JSON:"
    )

    llm_response = llm_service.complete(prompt=prompt)
    try:
        structured_data = json.loads(llm_response)
    except json.JSONDecodeError:
        structured_data = {}
    
    return structured_data


def extract_text_from_pdf(uploaded_pdf):
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    text = []
    for page in doc:
        text.append(page.get_text())
    return "\n".join(text)

def extract_text_from_docx(uploaded_docx):
    document = docx.Document(uploaded_docx)
    return "\n".join([para.text for para in document.paragraphs])

def extract_text_from_txt(uploaded_txt):
    return uploaded_txt.read().decode("utf-8", errors="ignore")

def extract_uploaded_file(uploaded_file):
    ext = uploaded_file.name.split(".")[-1].lower()
    if ext == "pdf":
        raw_text = extract_text_from_pdf(uploaded_file)
    elif ext == "docx":
        raw_text = extract_text_from_docx(uploaded_file)
    elif ext == "txt":
        raw_text = extract_text_from_txt(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    return clean_text(raw_text)

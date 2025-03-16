import streamlit as st
import requests
import os
import re
import json
import tempfile
import PyPDF2
import docx
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Retrieve API key from .env
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("❌ Missing OpenAI API Key. Check `.env` file.")


def store_in_state(key, value):
    """
    Shortcut for st.session_state[key] = value.
    """
    st.session_state[key] = value

def get_from_session_state(key, default=None):
    """
    Shortcut for retrieving st.session_state[key], or a default.
    """
    return st.session_state.get(key, default)

def safe_int(val, default=0):
    """
    Attempt to parse int from val. If it fails, return default.
    """
    try:
        return int(val)
    except:
        return default

##################################
# FILE PROCESSING
##################################
def process_uploaded_file(uploaded_file):
    """
    If a user uploads a PDF/DOCX/TXT, read it 
    and return a dict: {"job_description": <text>}.
    """
    if not uploaded_file:
        return {}
    filename = uploaded_file.name.lower()

    # Create temp file
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        path = tmp.name

    text_data = ""
    if filename.endswith(".pdf"):
        text_data = extract_text_from_pdf(path)
    elif filename.endswith(".docx"):
        text_data = extract_text_from_docx(path)
    elif filename.endswith(".txt"):
        text_data = extract_text_from_txt(path)

    try:
        os.remove(path)
    except:
        pass

    return {"job_description": text_data}

def extract_text_from_pdf(path):
    """
    Reads all pages from a PDF, merging text with newlines.
    """
    text_data = ""
    with open(path,"rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text_data += page.extract_text() + "\n"
    return text_data

def extract_text_from_docx(path):
    """
    Reads all paragraphs from a docx file.
    """
    d = docx.Document(path)
    return "\n".join([p.text for p in d.paragraphs])

def extract_text_from_txt(path):
    """
    Simple read of a text file as string.
    """
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def extract_content_from_url(url):
    """
    Makes a GET request, strips out HTML tags via regex.
    """
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return re.sub("<.*?>","", r.text)
    except:
        pass
    return ""

##################################
# LLaMA Non-Stream
##################################
def fetch_from_llama(prompt: str, model="llama3.2:3b", num_ctx=512) -> str:
    """
    Non-stream approach to local LLaMA (Ollama).
    We parse line-by-line JSON from server, 
    appending the 'response' field each time.
    """
    url = "http://127.0.0.1:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "num_ctx": num_ctx,
        "num_predict": 256,
        "stream": False
    }
    try:
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        lines = r.text.strip().splitlines()
        final_text = []
        for line in lines:
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                st.warning(f"Could not parse line as JSON:\n{line[:100]}")
                continue
            if "response" in data:
                final_text.append(data["response"])
        if not final_text:
            st.error("No 'response' in local LLaMA output.")
            return ""
        return "".join(final_text)
    except requests.exceptions.RequestException as e:
        st.error(f"Local LLaMA error: {e}")
        return ""

##################################
# JSON Parsing & 'Analyse'
##################################
def parse_model_json(text: str):
    """
    If we want only valid JSON, we find the first { ... } in text. 
    """
    cleaned = text.replace("```json","").replace("```","").strip()
    matches = re.findall(r"\{.*?\}", cleaned, re.DOTALL)
    if not matches:
        return None
    try:
        return json.loads(matches[0])
    except:
        return None

def analyze_uploaded_sources():
    """
    Combine URL + file content from session, 
    prompt the LLM for JSON job details, 
    parse & store them in session state.
    """
    combined_text = ""
    input_url = get_from_session_state("input_url","")
    if input_url:
        combined_text += extract_content_from_url(input_url)

    file_content = get_from_session_state("uploaded_file",{})
    if file_content and "job_description" in file_content:
        combined_text += "\n" + file_content["job_description"]

    if not combined_text.strip():
        st.warning("No text found to analyse.")
        return

    extraction_prompt = f"""
    You are an AI that extracts structured job or company details from the text below.
    Return ONLY valid JSON with these keys:
      "company_name","location","company_website","technologies_used",
      "travel_required","remote_policy","tasks","salary_range",
      "benefits","learning_opportunities","health_benefits".
    If data is not found, use an empty string.

    Text to analyse:
    {combined_text}
    """

    choice = st.session_state.get("llm_choice","openai_3.5")
    if choice.startswith("openai"):
        from llm_choice import get_llm
        response_text = get_llm()(extraction_prompt)
    else:
        response_text = fetch_from_llama(extraction_prompt)

    parsed_data = parse_model_json(response_text)
    if not parsed_data:
        st.error("❌ Failed to parse JSON from AI response.")
        return

    for k, v in parsed_data.items():
        store_in_state(k, v)

    st.success("✅ Successfully auto-filled fields from text!")

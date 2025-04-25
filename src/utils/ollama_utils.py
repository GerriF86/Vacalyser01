import requests
import json
import streamlit as st

OLLAMA_API_URL = "http://127.0.0.1:11434"

def fetch_from_ollama(prompt: str, model="llama3.2:3b", num_ctx=512, num_predict=256) -> str:
    """
    Calls Ollama's /api/generate endpoint with a prompt and model params.
    Returns the model's text output as a single string.
    """
    url = f"{OLLAMA_API_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "num_ctx": num_ctx,
        "num_predict": num_predict,
        "stream": False
    }
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()

        lines = response.text.strip().splitlines()
        final_text = []
        for line in lines:
            try:
                data = json.loads(line)
                if "response" in data:
                    final_text.append(data["response"])
            except json.JSONDecodeError:
                # If the line isn't valid JSON, ignore
                pass

        # Join all partial responses into one final string
        return "".join(final_text)

    except requests.exceptions.RequestException as e:
        st.error(f"Error contacting Ollama /api/generate: {e}")
        return ""
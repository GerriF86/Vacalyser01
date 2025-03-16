import streamlit as st
import openai
from functions import fetch_from_llama
import os
from dotenv import load_dotenv

def get_llm():
    """
    Returns a function that calls either:
    - local LLaMA (fetch_from_llama) 
    - or OpenAI ChatCompletion
    based on st.session_state["llm_choice"].
    """
    choice = st.session_state.get("llm_choice", "openai_3.5")
    if choice.startswith("openai"):
        return _fetch_openai_chat
    else:
        return _fetch_local_llama

def _fetch_openai_chat(prompt: str) -> str:
    """
    Uses openai.ChatCompletion with the API key from .env file.
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")

    if not openai.api_key:
        raise ValueError("❌ Missing OpenAI API Key. Check `.env` file.")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"OpenAI error: {e}"

def _fetch_local_llama(prompt: str) -> str:
    """
    If the user wants local LLaMA, call fetch_from_llama from functions.py.
    """
    return fetch_from_llama(prompt)

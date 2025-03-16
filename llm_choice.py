import streamlit as st
import openai
from functions import fetch_from_llama

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
    Makes an openai.ChatCompletion call, 
    grabbing the main text from .choices[0].message["content"].
    """
    openai.api_key = st.secrets.get("OPENAI_API_KEY","")
    model = "gpt-3.5-turbo"
    if st.session_state["llm_choice"] == "openai_o3_mini":
        model = "o3-mini"  # hypothetical or fine-tuned

    system_msg = (
        "You are an AI assistant returning answers in plain text. "
        "We'll specify if we want JSON. Provide direct responses."
    )
    try:
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
            ],
            temperature=st.session_state.get("model_temperature",0.2),
        )
        return resp.choices[0].message["content"]
    except Exception as e:
        st.error(f"OpenAI Chat error: {e}")
        return str(e)

def _fetch_local_llama(prompt: str) -> str:
    """
    If the user wants local LLaMA, call fetch_from_llama from functions.py.
    """
    return fetch_from_llama(prompt)

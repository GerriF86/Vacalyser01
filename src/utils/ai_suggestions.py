# ai_suggestions.py
import streamlit as st
from src.services.llm_service import LLMService

def suggest_improvements_for_job_description(job_description: str) -> str:
    """
    Use an LLM to suggest improvements for the job description.
    """
    if not job_description.strip():
        return ""
    llm = LLMService()
    prompt = f"Please review the job description below and suggest improvements:\n\n{job_description}"
    try:
        return llm.complete(prompt=prompt, system_message="You are an AI assistant.")
    except Exception as e:
        st.error(f"Error getting suggestions: {e}")
        return ""

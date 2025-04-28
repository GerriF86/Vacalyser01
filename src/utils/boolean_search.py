# src/utils/boolean_search.py
from src.utils.llm_service import LLMService

def generate_boolean_search(key_skills: list, job_title: str) -> str:
    """
    Generate a Boolean search string given key skills.
    """
    llm = LLMService()
    skills_str = ", ".join(key_skills) if key_skills else job_title
    prompt = (
        f"Generate a Boolean search query to find candidates with skills: {skills_str}. "
        "Use AND, OR, NOT operators and include synonyms if applicable."
    )
    result = llm.complete(prompt=prompt, system_message="You are an expert sourcer.")
    return result

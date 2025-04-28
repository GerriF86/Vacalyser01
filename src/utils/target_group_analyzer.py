# src/utils/target_group_analyzer.py
from src.utils.llm_service import LLMService

def analyze_target_group(job_title: str, company: str, role_description: str) -> str:
    """
    Use an LLM to describe the ideal target candidate group for this role.
    """
    llm = LLMService()  # Default settings (local or OpenAI)
    prompt = (
        f"Based on the job title \"{job_title}\" at {company} and the following role description, "
        "describe the ideal candidate demographics and skill background (target group):\n\n"
        f"{role_description}\n\n"
        "Answer in a clear paragraph."
    )
    result = llm.complete(prompt=prompt, system_message="You are a recruiter assistant.")
    return result

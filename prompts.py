# prompts.py

from llm_choice import fetch_from_llama
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env
def generate_job_ad(session_data):
    """
    Generate a job ad from the session data.
    This is a simple version. Extend or refine as needed.
    """
    job_title = session_data.get("job_title", "No Title")
    company_name = session_data.get("company_name", "No Company")
    location = session_data.get("location", "")
    benefits = session_data.get("benefits", "")
    tasks = session_data.get("tasks", "")
    responsibilities = session_data.get("responsibility_distribution", "")
    
    prompt = f"""
    You are an AI specialized in HR. Create a compelling job ad for the following role:
    Job Title: {job_title}
    Company: {company_name}
    Location: {location}
    Responsibilities: {responsibilities}
    Key Tasks: {tasks}
    Benefits: {benefits}
    Make it engaging and concise. Return a plain text version.
    """
    return fetch_from_llama(prompt)

def generate_interview_guide(job_details: dict, perspective: str = "HR") -> str:
    """
    Generates a more sophisticated interview preparation guide, with recommended questions,
    alignment to responsibilities/tasks, etc.
    """
    title = job_details.get("job_title", "N/A")
    responsibilities = job_details.get("responsibility_distribution", [])
    tasks = job_details.get("tasks", [])
    challenges = job_details.get("job_challenges", [])
    interview_stages = job_details.get("interview_stages", 1)

    resp_str = "\n- ".join(responsibilities) if isinstance(responsibilities, list) else responsibilities
    tasks_str = "\n- ".join(tasks) if isinstance(tasks, list) else tasks
    chal_str = "\n- ".join(challenges) if isinstance(challenges, list) else challenges

    guide_text = f"""
### Interview Guide: {title} ({perspective} Perspective)

**Number of Interview Rounds**: {interview_stages}

#### Role Overview
- Responsibilities:
{resp_str}

- Core Tasks:
{tasks_str}

- Typical Challenges:
{chal_str}

---

### Suggested Questions

**1) Relevance to Responsibilities**
- Which of the above responsibilities have you handled in prior roles?
- How do you prioritize tasks when multiple responsibilities overlap?

**2) Core Tasks Insight**
- Walk us through a typical day where you'd handle {', '.join(tasks)}.
- What strategies do you use to stay organized?

**3) Handling Challenges**
- Have you encountered a similar challenge like {', '.join(challenges)} before?
- How did you approach it, and what was the outcome?

**4) Culture & Team Fit**
- How do you adapt to departmental goals or collaborate across departments?
- Provide an example of conflict resolution in a team setting.

**5) Motivation & Goals**
- What draws you to {title} in our organization?
- Where do you see your professional development aligning with our L&D opportunities?

---

### Interview Flow
1. **Intro** (5-10 mins)
   - Warm welcome, overview of role, candidate’s background summary.
2. **Deep Dive** (20+ mins)
   - Discuss responsibilities, tasks, challenges in detail.
3. **Q&A** (10+ mins)
   - Candidate’s questions about company, culture, next steps.
4. **Wrap-Up** (5 mins)
   - Thank the candidate, outline timeline, set expectations for follow-up.

---

Thank you for using this Interview Guide. Adapt questions or add more role-specific queries
based on your organization’s unique needs. Good luck!
    """
    return guide_text.strip()

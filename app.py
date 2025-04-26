import streamlit as st
import os
from dotenv import load_dotenv
from src.utils import extraction, ollama_utils, openai_utils, scraping, preprocessing
from src.session_state import initialize_session_state
from src.services.llm_service import LLMService
import openai
from openai import OpenAI


# Load environment variables
load_dotenv()

initialize_session_state()
# Initialize API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11434")

###############################################################################
# Helper Functions & Placeholders
###############################################################################

def apply_base_styling():
    """
    Placeholder: If you have global CSS or styling calls, put them here.
    """
    # Example: st.markdown("<style>...</style>", unsafe_allow_html=True)
    pass

def show_sidebar_links():
    """
    Placeholder: If you have a sidebar with nav links or branding, define it here.
    """
    st.sidebar.title("Vacalyser Wizard")
    st.sidebar.info("Use the steps below to create a job vacancy.")
    # Possibly put other links or disclaimers.

def get_from_session_state(key, default=None):
    """Helper to read from session_state safely."""
    return st.session_state.get(key, default)

def store_in_state(key, value):
    """Helper to write into session_state."""
    st.session_state[key] = value

def parse_file(uploaded_file, file_name: str = "") -> str:
    """
    Parse the contents of an uploaded file (PDF, DOCX, or TXT).
    Return the raw text. You could also call advanced logic from src/utils/extraction.py.
    """
    import os
    ext = os.path.splitext(file_name)[1].lower()
    if ext == ".pdf":
        from src.utils.extraction import extract_text_from_pdf
        return extract_text_from_pdf(uploaded_file)
    elif ext == ".docx":
        import docx
        document = docx.Document(uploaded_file)
        return "\n".join([p.text for p in document.paragraphs])
    elif ext == ".txt":
        return uploaded_file.read().decode("utf-8", errors="ignore")
    else:
        return ""

def match_and_store_keys(raw_text: str, session_keys: list):
    """
    Trivial example to parse lines containing specific labels,
    then store the remainder of the line in st.session_state.

    For a real system, consider:
    1) Using GPT to return JSON with all fields, then parse & store.
    2) Using advanced regex to handle multiple lines or partial info.
    3) Handling edge cases, partial matches, synonyms, etc.
    """

    # Map each st.session_state key -> a search label in raw_text
    # The left side is our session_state key; the right side is the literal text prefix to find.
    label_map = {
        "job_title": "Job Title:",
        "company_name": "Company Name:",
        "brand_name": "Brand Name:",
        "headquarters_location": "HQ Location:",
        "company_website": "Company Website:",
        "date_of_employment_start": "Date of Employment Start:",
        "job_type": "Job Type:",
        "contract_type": "Contract Type:",
        "job_level": "Job Level:",
        "city": "City (Job Location):",
        "team_structure": "Team Structure:",
        "role_description": "Role Description:",
        "reports_to": "Reports To:",
        "supervises": "Supervises:",
        "role_type": "Role Type:",
        "role_priority_projects": "Role Priority Projects:",
        "travel_requirements": "Travel Requirements:",
        "work_schedule": "Work Schedule:",
        "role_keywords": "Role Keywords:",
        "decision_making_authority": "Decision Making Authority:",
        "role_performance_metrics": "Role Performance Metrics:",
        "task_list": "Task List:",
        "key_responsibilities": "Key Responsibilities:",
        "technical_tasks": "Technical Tasks:",
        "managerial_tasks": "Managerial Tasks:",
        "administrative_tasks": "Administrative Tasks:",
        "customer_facing_tasks": "Customer-Facing Tasks:",
        "internal_reporting_tasks": "Internal Reporting Tasks:",
        "performance_tasks": "Performance Tasks:",
        "innovation_tasks": "Innovation Tasks:",
        "task_prioritization": "Task Prioritization:",
        "hard_skills": "Hard Skills:",
        "soft_skills": "Soft Skills:",
        "must_have_skills": "Must-Have Skills:",
        "nice_to_have_skills": "Nice-to-Have Skills:",
        "certifications_required": "Certifications Required:",
        "language_requirements": "Language Requirements:",
        "tool_proficiency": "Tool Proficiency:",
        "domain_expertise": "Domain Expertise:",
        "leadership_competencies": "Leadership Competencies:",
        "technical_stack": "Technical Stack:",
        "industry_experience": "Industry Experience:",
        "analytical_skills": "Analytical Skills:",
        "communication_skills": "Communication Skills:",
        "project_management_skills": "Project Management Skills:",
        "soft_requirement_details": "Additional Soft Requirements:",
        "visa_sponsorship": "Visa Sponsorship:",
        "salary_range": "Salary Range:",
        "currency": "Currency:",
        "pay_frequency": "Pay Frequency:",
        "commission_structure": "Commission Structure:",
        "bonus_scheme": "Bonus Scheme:",
        "vacation_days": "Vacation Days:",
        "flexible_hours": "Flexible Hours:",
        "remote_work_policy": "Remote Work Policy:",
        "relocation_assistance": "Relocation Assistance:",
        "childcare_support": "Childcare Support:",
        "recruitment_steps": "Recruitment Steps:",
        "recruitment_timeline": "Recruitment Timeline:",
        "number_of_interviews": "Number of Interviews:",
        "interview_format": "Interview Format:",
        "assessment_tests": "Assessment Tests:",
        "onboarding_process_overview": "Onboarding Process Overview:",
        "recruitment_contact_email": "Recruitment Contact Email:",
        "recruitment_contact_phone": "Recruitment Contact Phone:",
        "application_instructions": "Application Instructions:",
        "parsed_data_raw": "Parsed Data Raw:",
        "language_of_ad": "Language of Ad:",
        "translation_required": "Translation Required:",
        "employer_branding_elements": "Employer Branding Elements:",
        "desired_publication_channels": "Desired Publication Channels:",
        "internal_job_id": "Internal Job ID:",
        "ad_seniority_tone": "Ad Seniority Tone:",
        "ad_length_preference": "Ad Length Preference:",
        "deadline_urgency": "Deadline Urgency:",
        "company_awards": "Company Awards:",
        "diversity_inclusion_statement": "Diversity & Inclusion Statement:",
        "legal_disclaimers": "Legal Disclaimers:",
        "social_media_links": "Social Media Links:",
        "video_introduction_option": "Video Introduction Option:",
        "comments_internal": "Comments (Internal):",
    }

    # For each key in our map, try to find it in 'raw_text'.
    for key, label in label_map.items():
        if label in raw_text:
            # Example approach: split after the label, then take until newline
            line = raw_text.split(label, 1)[1].split("\n", 1)[0].strip()
            st.session_state[key] = line

    print("match_and_store_keys: Done extracting fields from raw_text")
SESSION_KEYS = [
        "job_title",
        "company_name",
        "brand_name",
        "headquarters_location",
        "company_website",
        "date_of_employment_start",
        "job_type",
        "contract_type",
        "job_level",
        "city",
        "team_structure",
        "role_description",
        "reports_to",
        "supervises",
        "role_type",
        "role_priority_projects",
        "travel_requirements",
        "work_schedule",
        "role_keywords",
        "decision_making_authority",
        "role_performance_metrics",
        "task_list",
        "key_responsibilities",
        "technical_tasks",
        "managerial_tasks",
        "administrative_tasks",
        "customer_facing_tasks",
        "internal_reporting_tasks",
        "performance_tasks",
        "innovation_tasks",
        "task_prioritization",
        "hard_skills",
        "soft_skills",
        "must_have_skills",
        "nice_to_have_skills",
        "certifications_required",
        "language_requirements",
        "tool_proficiency",
        "domain_expertise",
        "leadership_competencies",
        "technical_stack",
        "industry_experience",
        "analytical_skills",
        "communication_skills",
        "project_management_skills",
        "soft_requirement_details",
        "visa_sponsorship",
        "salary_range",
        "currency",
        "pay_frequency",
        "commission_structure",
        "bonus_scheme",
        "vacation_days",
        "flexible_hours",
        "remote_work_policy",
        "relocation_assistance",
        "childcare_support",
        "recruitment_steps",
        "recruitment_timeline",
        "number_of_interviews",
        "interview_format",
        "assessment_tests",
        "onboarding_process_overview",
        "recruitment_contact_email",
        "recruitment_contact_phone",
        "application_instructions",
        "parsed_data_raw",
        "language_of_ad",
        "translation_required",
        "employer_branding_elements",
        "desired_publication_channels",
        "internal_job_id",
        "ad_seniority_tone",
        "ad_length_preference",
        "deadline_urgency",
        "company_awards",
        "diversity_inclusion_statement",
        "legal_disclaimers",
        "social_media_links",
        "video_introduction_option",
        "comments_internal",
    ]

###############################################################################
# PAGE 1: Start Discovery (NEW)
###############################################################################
def start_discovery_page():
    """ Wizard Page 1: Start Discovery. """
    apply_base_styling()
    show_sidebar_links()

    # Example logo
    st.image("images/sthree.png", width=80)
    st.title("Vacalyser")

    client = OpenAI()                         # key from env / st.secrets
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello, world!"}],
        temperature=0.7,
        max_tokens=50,
    )
    st.write("GPT Example Response:", resp.choices[0].message.content)
  st.markdown(
        "**Enhancing hiring workflows** with intelligent suggestions and automations. "
        "We help teams fine-tune job postings and CVs efficiently for better hiring outcomes."
    )

    st.header("1) Start Discovery")
    st.write(
        "Enter a **Job Title**, optionally a link or an uploaded file. We'll auto-fill fields "
        "where possible after analysis."
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        job_title_val = get_from_session_state("job_title", "")
        job_title = st.text_input("Enter a **Job Title**", value=job_title_val)
        store_in_state("job_title", job_title)

        default_url = get_from_session_state("input_url", "http://www.")
        input_url = st.text_input("🔗 Link to a Job Ad / Company Website", value=default_url)
        store_in_state("input_url", input_url)

    with col2:
        uploaded_file = st.file_uploader("Upload Job Ad (PDF, DOCX, TXT)", ["pdf", "docx", "txt"])
        if uploaded_file:
            raw_text = extraction.extract_uploaded_file(uploaded_file)
            st.session_state["uploaded_file"] = raw_text
            st.success("File uploaded successfully.")

        if st.button("Analyse Sources"):
            raw_text = st.session_state.get("uploaded_file", "")
            if not raw_text:
                st.warning("Upload a file or enter URL first.")
                return

            keys = list(st.session_state.keys())
            extracted_info = extraction.extract_structured_info(raw_text, keys)
            st.session_state.update(extracted_info)
            st.success("Information extracted and fields populated.")
            
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Analyse Sources"):
            try:
                raw_text = get_from_session_state("uploaded_file", "")
                if not raw_text.strip():
                    st.warning("No file content found. Please upload a file or specify a link.")
                else:
                    match_and_store_keys(raw_text, SESSION_KEYS)
                    st.success("Keys extracted successfully from the uploaded file.")
            except Exception as err:
                st.error(f"Analysis failed: {err}")
            else:
                # Optionally remain on this page or automatically move to next
                st.experimental_rerun()

    #with c2:
        # On "Next ➡" button, move to step 2
      #  if st.button("Next ➡"):
       #     st.session_state["wizard_step"] += 1
       #     st.experimental_rerun()

###############################################################################
# PAGE 2: Basic Job & Company Info (Previously Step 1)
###############################################################################
def render_step_2():
    """
    Renamed from old "render_step_1" to "render_step_2" for continuity
    because now 'Start Discovery' is step_1.
    """
    st.title("Step 2: Basic Job & Company Info")
    # ... (same logic as your old Step 1, now Step 2)
    st.session_state["job_title"] = st.text_input(
        "Job Title",
        value=st.session_state["job_title"],
        placeholder="e.g. Data Scientist"
    )
    st.session_state["company_name"] = st.text_input(
        "Company Name",
        value=st.session_state["company_name"],
        placeholder="e.g. Tech Corp Ltd."
    )
    st.session_state["brand_name"] = st.text_input(
        "Brand Name",
        value=st.session_state["brand_name"],
        placeholder="If different from the company name"
    )
    st.session_state["headquarters_location"] = st.text_input(
        "Headquarters Location",
        value=st.session_state["headquarters_location"],
        placeholder="e.g. Berlin, Germany"
    )
    st.session_state["company_website"] = st.text_input(
        "Company Website",
        value=st.session_state["company_website"],
        placeholder="e.g. https://www.techcorp.com"
    )
    st.session_state["date_of_employment_start"] = st.text_input(
        "Preferred/Earliest Start Date",
        value=st.session_state["date_of_employment_start"],
        placeholder="e.g. ASAP or 2025-05-01"
    )

    st.session_state["job_type"] = st.selectbox(
        "Job Type",
        ["Full-Time", "Part-Time", "Internship", "Freelance", "Volunteer", "Other"],
        index=0
    )
    st.session_state["contract_type"] = st.selectbox(
        "Contract Type",
        ["Permanent", "Fixed-Term", "Contract/Freelance", "Other"],
        index=0
    )
    st.session_state["job_level"] = st.selectbox(
        "Job Level",
        ["Entry-level", "Mid-level", "Senior", "Director", "C-level", "Other"],
        index=0
    )
    st.session_state["city"] = st.text_input(
        "City (Job Location)",
        value=st.session_state["city"],
        placeholder="e.g. Berlin"
    )
    st.session_state["team_structure"] = st.text_area(
        "Team Structure",
        value=st.session_state["team_structure"],
        placeholder="Describe how the team is set up..."
    )


###############################################################################
# PAGE 3: Role Definition (old Step 2)
###############################################################################
def render_step_3():
    st.title("Step 3: Role Definition")
    st.session_state["role_description"] = st.text_area(
        "Role Description",
        value=st.session_state["role_description"],
        placeholder="High-level summary of the role..."
    )
    st.session_state["reports_to"] = st.text_input(
        "Reports To",
        value=st.session_state["reports_to"],
        placeholder="Manager position or name..."
    )
    st.session_state["supervises"] = st.text_area(
        "Supervises",
        value=st.session_state["supervises"],
        placeholder="List any staff or functions this role manages."
    )
    st.session_state["role_type"] = st.selectbox(
        "Role Type",
        ["Individual Contributor", "Team Lead", "Manager", "Director", "Executive", "Other"],
        index=0
    )
    st.session_state["role_priority_projects"] = st.text_area(
        "Priority Projects",
        value=st.session_state["role_priority_projects"],
        placeholder="High-priority projects for this role..."
    )
    st.session_state["travel_requirements"] = st.text_input(
        "Travel Requirements",
        value=st.session_state["travel_requirements"],
        placeholder="e.g. up to 20% travel"
    )
    st.session_state["work_schedule"] = st.text_input(
        "Work Schedule",
        value=st.session_state["work_schedule"],
        placeholder="e.g. 9-5 M-F, shift-based, etc."
    )
    st.session_state["role_keywords"] = st.text_area(
        "Role Keywords",
        value=st.session_state["role_keywords"],
        placeholder="Keyword tags for analytics or searching."
    )
    st.session_state["decision_making_authority"] = st.text_input(
        "Decision-Making Authority",
        value=st.session_state["decision_making_authority"],
        placeholder="e.g. Budget approvals up to $10k"
    )
    st.session_state["role_performance_metrics"] = st.text_area(
        "Role Performance Metrics",
        value=st.session_state["role_performance_metrics"],
        placeholder="KPIs or success measures..."
    )

###############################################################################
# PAGE 4: Tasks & Responsibilities (old Step 3)
###############################################################################
def render_step_4():
    st.title("Step 4: Tasks & Responsibilities")
    st.session_state["task_list"] = st.text_area(
        "General Task List",
        value=st.session_state["task_list"],
        placeholder="Bullet-point list of day-to-day tasks..."
    )
    st.session_state["key_responsibilities"] = st.text_area(
        "Key Responsibilities",
        value=st.session_state["key_responsibilities"],
        placeholder="High-level responsibilities..."
    )
    st.session_state["technical_tasks"] = st.text_area(
        "Technical Tasks",
        value=st.session_state["technical_tasks"],
        placeholder="Specialized or technical tasks..."
    )
    st.session_state["managerial_tasks"] = st.text_area(
        "Managerial Tasks",
        value=st.session_state["managerial_tasks"],
        placeholder="Supervising staff, performance reviews..."
    )
    st.session_state["administrative_tasks"] = st.text_area(
        "Administrative Tasks",
        value=st.session_state["administrative_tasks"],
        placeholder="Reporting, data entry, scheduling..."
    )
    st.session_state["customer_facing_tasks"] = st.text_area(
        "Customer-Facing Tasks",
        value=st.session_state["customer_facing_tasks"],
        placeholder="Interactions with clients, phone calls..."
    )
    st.session_state["internal_reporting_tasks"] = st.text_area(
        "Internal Reporting Tasks",
        value=st.session_state["internal_reporting_tasks"],
        placeholder="Define who receives updates from this role..."
    )
    st.session_state["performance_tasks"] = st.text_area(
        "Performance-Related Tasks",
        value=st.session_state["performance_tasks"],
        placeholder="Tied directly to performance metrics..."
    )
    st.session_state["innovation_tasks"] = st.text_area(
        "Innovation Tasks",
        value=st.session_state["innovation_tasks"],
        placeholder="R&D, brainstorming, product innovation..."
    )
    st.session_state["task_prioritization"] = st.text_area(
        "Task Prioritization",
        value=st.session_state["task_prioritization"],
        placeholder="Rank or priority of tasks..."
    )

###############################################################################
# PAGE 5: Skills & Competencies (old Step 4)
###############################################################################
def render_step_5():
    st.title("Step 5: Skills & Competencies")
    st.session_state["hard_skills"] = st.text_area(
        "Hard Skills",
        value=st.session_state["hard_skills"],
        placeholder="Technical or domain-specific skills..."
    )
    st.session_state["soft_skills"] = st.text_area(
        "Soft Skills",
        value=st.session_state["soft_skills"],
        placeholder="Communication, teamwork, leadership..."
    )
    st.session_state["must_have_skills"] = st.text_area(
        "Must-Have Skills",
        value=st.session_state["must_have_skills"],
        placeholder="Absolute requirements..."
    )
    st.session_state["nice_to_have_skills"] = st.text_area(
        "Nice-to-Have Skills",
        value=st.session_state["nice_to_have_skills"],
        placeholder="Additional beneficial skills..."
    )
    st.session_state["certifications_required"] = st.text_area(
        "Certifications Required",
        value=st.session_state["certifications_required"],
        placeholder="e.g. PMP, CPA..."
    )
    st.session_state["language_requirements"] = st.text_area(
        "Language Requirements",
        value=st.session_state["language_requirements"],
        placeholder="e.g. English C1, German B2..."
    )
    st.session_state["tool_proficiency"] = st.text_area(
        "Tool Proficiency",
        value=st.session_state["tool_proficiency"],
        placeholder="Specific platforms needed: AWS, Excel..."
    )
    st.session_state["domain_expertise"] = st.text_area(
        "Domain Expertise",
        value=st.session_state["domain_expertise"],
        placeholder="ML, marketing analytics, etc."
    )
    st.session_state["leadership_competencies"] = st.text_area(
        "Leadership Competencies",
        value=st.session_state["leadership_competencies"],
        placeholder="For roles that include team leadership..."
    )
    st.session_state["technical_stack"] = st.text_area(
        "Technical Stack",
        value=st.session_state["technical_stack"],
        placeholder="Applicable for dev roles..."
    )
    st.session_state["industry_experience"] = st.text_input(
        "Industry Experience",
        value=st.session_state["industry_experience"],
        placeholder="Years in relevant industry..."
    )
    st.session_state["analytical_skills"] = st.text_input(
        "Analytical Skills",
        value=st.session_state["analytical_skills"],
        placeholder="Data analysis, critical thinking..."
    )
    st.session_state["communication_skills"] = st.text_input(
        "Communication Skills",
        value=st.session_state["communication_skills"],
        placeholder="Written, oral, cross-team..."
    )
    st.session_state["project_management_skills"] = st.text_input(
        "Project Management Skills",
        value=st.session_state["project_management_skills"],
        placeholder="Planning, resource allocation, etc."
    )
    st.session_state["soft_requirement_details"] = st.text_area(
        "Additional Soft Requirements",
        value=st.session_state["soft_requirement_details"],
        placeholder="Empathy, collaboration, etc."
    )
    st.session_state["visa_sponsorship"] = st.selectbox(
        "Visa Sponsorship?",
        ["No", "Yes", "Case-by-Case"],
        index=0
    )

###############################################################################
# PAGE 6: Compensation & Benefits (old Step 5)
###############################################################################
def render_step_6():
    st.title("Step 6: Compensation & Benefits")
    st.session_state["salary_range"] = st.text_input(
        "Salary Range",
        value=st.session_state["salary_range"],
        placeholder="e.g. 50,000 - 60,000"
    )
    st.session_state["currency"] = st.selectbox(
        "Currency",
        ["EUR", "USD", "GBP", "Other"],
        index=0
    )
    st.session_state["pay_frequency"] = st.selectbox(
        "Pay Frequency",
        ["Annual", "Monthly", "Bi-weekly", "Weekly", "Other"],
        index=0
    )
    st.session_state["commission_structure"] = st.text_input(
        "Commission Structure",
        value=st.session_state["commission_structure"],
        placeholder="Sales commission details..."
    )
    st.session_state["bonus_scheme"] = st.text_input(
        "Bonus Scheme",
        value=st.session_state["bonus_scheme"],
        placeholder="Performance-based annual bonus..."
    )
    st.session_state["vacation_days"] = st.text_input(
        "Vacation Days",
        value=st.session_state["vacation_days"],
        placeholder="Number of paid vacation days..."
    )
    st.session_state["flexible_hours"] = st.selectbox(
        "Flexible Hours?",
        ["No", "Yes", "Partial/Flex Schedule"],
        index=0
    )
    st.session_state["remote_work_policy"] = st.selectbox(
        "Remote Work Policy",
        ["On-site", "Hybrid", "Full Remote", "Other"],
        index=0
    )
    st.session_state["relocation_assistance"] = st.selectbox(
        "Relocation Assistance?",
        ["No", "Yes", "Case-by-Case"],
        index=0
    )
    st.session_state["childcare_support"] = st.selectbox(
        "Childcare Support?",
        ["No", "Yes", "Case-by-Case"],
        index=0
    )

###############################################################################
# PAGE 7: Recruitment Process (old Step 6)
###############################################################################
def render_step_7():
    st.title("Step 7: Recruitment Process")
    st.session_state["recruitment_steps"] = st.text_area(
        "Recruitment Steps",
        value=st.session_state["recruitment_steps"],
        placeholder="e.g. 2 interview rounds + 1 assignment..."
    )
    st.session_state["recruitment_timeline"] = st.text_input(
        "Recruitment Timeline",
        value=st.session_state["recruitment_timeline"],
        placeholder="Approx. time from application to final decision..."
    )
    st.session_state["number_of_interviews"] = st.text_input(
        "Number of Interviews",
        value=st.session_state["number_of_interviews"]
    )
    st.session_state["interview_format"] = st.text_input(
        "Interview Format",
        value=st.session_state["interview_format"],
        placeholder="In-person, phone, video..."
    )
    st.session_state["assessment_tests"] = st.text_area(
        "Assessment Tests",
        value=st.session_state["assessment_tests"],
        placeholder="Codility tests, writing samples, etc."
    )
    st.session_state["onboarding_process_overview"] = st.text_area(
        "Onboarding Process Overview",
        value=st.session_state["onboarding_process_overview"],
        placeholder="Basic overview of the onboarding..."
    )
    st.session_state["recruitment_contact_email"] = st.text_input(
        "Recruitment Contact Email",
        value=st.session_state["recruitment_contact_email"]
    )
    st.session_state["recruitment_contact_phone"] = st.text_input(
        "Recruitment Contact Phone",
        value=st.session_state["recruitment_contact_phone"]
    )
    st.session_state["application_instructions"] = st.text_area(
        "Application Instructions",
        value=st.session_state["application_instructions"],
        placeholder="Apply via website, send CV to X..."
    )

###############################################################################
# PAGE 8: Additional Info & Final Summary (old Step 7)
###############################################################################
def render_step_8():
    st.title("Step 8: Additional Information & Final Review")
    st.subheader("Additional Metadata")
    st.session_state["parsed_data_raw"] = st.text_area(
        "Parsed Data (Raw)",
        value=st.session_state["parsed_data_raw"],
        placeholder="Optional: raw text or JSON from LLM parse..."
    )
    st.session_state["language_of_ad"] = st.text_input(
        "Language of Ad",
        value=st.session_state["language_of_ad"],
        placeholder="e.g. English, German..."
    )
    st.session_state["translation_required"] = st.selectbox(
        "Translation Required?",
        ["No", "Yes"],
        index=0
    )
    st.session_state["employer_branding_elements"] = st.text_area(
        "Employer Branding Elements",
        value=st.session_state["employer_branding_elements"]
    )
    st.session_state["desired_publication_channels"] = st.text_area(
        "Desired Publication Channels",
        value=st.session_state["desired_publication_channels"]
    )
    st.session_state["internal_job_id"] = st.text_input(
        "Internal Job ID",
        value=st.session_state["internal_job_id"]
    )
    st.session_state["ad_seniority_tone"] = st.selectbox(
        "Ad Seniority Tone",
        ["Casual", "Formal", "Neutral", "Enthusiastic"],
        index=0
    )
    st.session_state["ad_length_preference"] = st.selectbox(
        "Ad Length Preference",
        ["Short & Concise", "Detailed", "Flexible"],
        index=0
    )
    st.session_state["deadline_urgency"] = st.text_input(
        "Deadline Urgency",
        value=st.session_state["deadline_urgency"]
    )
    st.session_state["company_awards"] = st.text_area(
        "Company Awards",
        value=st.session_state["company_awards"]
    )
    st.session_state["diversity_inclusion_statement"] = st.text_area(
        "Diversity & Inclusion Statement",
        value=st.session_state["diversity_inclusion_statement"]
    )
    st.session_state["legal_disclaimers"] = st.text_area(
        "Legal Disclaimers",
        value=st.session_state["legal_disclaimers"]
    )
    st.session_state["social_media_links"] = st.text_area(
        "Social Media Links",
        value=st.session_state["social_media_links"]
    )
    st.session_state["video_introduction_option"] = st.selectbox(
        "Video Introduction Option?",
        ["No", "Yes"],
        index=0
    )
    st.session_state["comments_internal"] = st.text_area(
        "Comments (Internal)",
        value=st.session_state["comments_internal"]
    )

    # Final summary with the missing data (instead of # etc...)
    st.subheader("Final Summary (Preview)")

    st.markdown(f"**Job Title:** {st.session_state['job_title']}")
    st.markdown(f"**Company Name:** {st.session_state['company_name']}")
    st.markdown(f"**Brand Name:** {st.session_state['brand_name']}")
    st.markdown(f"**HQ Location:** {st.session_state['headquarters_location']}")
    st.markdown(f"**Company Website:** {st.session_state['company_website']}")
    st.markdown(f"**Date of Employment Start:** {st.session_state['date_of_employment_start']}")
    st.markdown(f"**Job Type:** {st.session_state['job_type']}")
    st.markdown(f"**Contract Type:** {st.session_state['contract_type']}")
    st.markdown(f"**Job Level:** {st.session_state['job_level']}")
    st.markdown(f"**City (Job Location):** {st.session_state['city']}")
    st.markdown(f"**Team Structure:** {st.session_state['team_structure']}")
    st.markdown("---")

    st.markdown(f"**Role Description:** {st.session_state['role_description']}")
    st.markdown(f"**Reports To:** {st.session_state['reports_to']}")
    st.markdown(f"**Supervises:** {st.session_state['supervises']}")
    st.markdown(f"**Role Type:** {st.session_state['role_type']}")
    st.markdown(f"**Role Priority Projects:** {st.session_state['role_priority_projects']}")
    st.markdown(f"**Travel Requirements:** {st.session_state['travel_requirements']}")
    st.markdown(f"**Work Schedule:** {st.session_state['work_schedule']}")
    st.markdown(f"**Role Keywords:** {st.session_state['role_keywords']}")
    st.markdown(f"**Decision Making Authority:** {st.session_state['decision_making_authority']}")
    st.markdown(f"**Role Performance Metrics:** {st.session_state['role_performance_metrics']}")
    st.markdown("---")

    st.markdown(f"**Task List:** {st.session_state['task_list']}")
    st.markdown(f"**Key Responsibilities:** {st.session_state['key_responsibilities']}")
    st.markdown(f"**Technical Tasks:** {st.session_state['technical_tasks']}")
    st.markdown(f"**Managerial Tasks:** {st.session_state['managerial_tasks']}")
    st.markdown(f"**Administrative Tasks:** {st.session_state['administrative_tasks']}")
    st.markdown(f"**Customer-Facing Tasks:** {st.session_state['customer_facing_tasks']}")
    st.markdown(f"**Internal Reporting Tasks:** {st.session_state['internal_reporting_tasks']}")
    st.markdown(f"**Performance Tasks:** {st.session_state['performance_tasks']}")
    st.markdown(f"**Innovation Tasks:** {st.session_state['innovation_tasks']}")
    st.markdown(f"**Task Prioritization:** {st.session_state['task_prioritization']}")
    st.markdown("---")

    st.markdown(f"**Hard Skills:** {st.session_state['hard_skills']}")
    st.markdown(f"**Soft Skills:** {st.session_state['soft_skills']}")
    st.markdown(f"**Must-Have Skills:** {st.session_state['must_have_skills']}")
    st.markdown(f"**Nice-to-Have Skills:** {st.session_state['nice_to_have_skills']}")
    st.markdown(f"**Certifications Required:** {st.session_state['certifications_required']}")
    st.markdown(f"**Language Requirements:** {st.session_state['language_requirements']}")
    st.markdown(f"**Tool Proficiency:** {st.session_state['tool_proficiency']}")
    st.markdown(f"**Domain Expertise:** {st.session_state['domain_expertise']}")
    st.markdown(f"**Leadership Competencies:** {st.session_state['leadership_competencies']}")
    st.markdown(f"**Technical Stack:** {st.session_state['technical_stack']}")
    st.markdown(f"**Industry Experience:** {st.session_state['industry_experience']}")
    st.markdown(f"**Analytical Skills:** {st.session_state['analytical_skills']}")
    st.markdown(f"**Communication Skills:** {st.session_state['communication_skills']}")
    st.markdown(f"**Project Management Skills:** {st.session_state['project_management_skills']}")
    st.markdown(f"**Additional Soft Requirements:** {st.session_state['soft_requirement_details']}")
    st.markdown(f"**Visa Sponsorship:** {st.session_state['visa_sponsorship']}")
    st.markdown("---")

    st.markdown(f"**Salary Range:** {st.session_state['salary_range']} {st.session_state['currency']}")
    st.markdown(f"**Pay Frequency:** {st.session_state['pay_frequency']}")
    st.markdown(f"**Commission Structure:** {st.session_state['commission_structure']}")
    st.markdown(f"**Bonus Scheme:** {st.session_state['bonus_scheme']}")
    st.markdown(f"**Vacation Days:** {st.session_state['vacation_days']}")
    st.markdown(f"**Flexible Hours:** {st.session_state['flexible_hours']}")
    st.markdown(f"**Remote Work Policy:** {st.session_state['remote_work_policy']}")
    st.markdown(f"**Relocation Assistance:** {st.session_state['relocation_assistance']}")
    st.markdown(f"**Childcare Support:** {st.session_state['childcare_support']}")
    st.markdown("---")

    st.markdown(f"**Recruitment Steps:** {st.session_state['recruitment_steps']}")
    st.markdown(f"**Recruitment Timeline:** {st.session_state['recruitment_timeline']}")
    st.markdown(f"**Number of Interviews:** {st.session_state['number_of_interviews']}")
    st.markdown(f"**Interview Format:** {st.session_state['interview_format']}")
    st.markdown(f"**Assessment Tests:** {st.session_state['assessment_tests']}")
    st.markdown(f"**Onboarding Process Overview:** {st.session_state['onboarding_process_overview']}")
    st.markdown(f"**Recruitment Contact Email:** {st.session_state['recruitment_contact_email']}")
    st.markdown(f"**Recruitment Contact Phone:** {st.session_state['recruitment_contact_phone']}")
    st.markdown(f"**Application Instructions:** {st.session_state['application_instructions']}")
    st.markdown("---")

    st.markdown(f"**Parsed Data Raw:** {st.session_state['parsed_data_raw']}")
    st.markdown(f"**Language of Ad:** {st.session_state['language_of_ad']}")
    st.markdown(f"**Translation Required:** {st.session_state['translation_required']}")
    st.markdown(f"**Employer Branding Elements:** {st.session_state['employer_branding_elements']}")
    st.markdown(f"**Desired Publication Channels:** {st.session_state['desired_publication_channels']}")
    st.markdown(f"**Internal Job ID:** {st.session_state['internal_job_id']}")
    st.markdown(f"**Ad Seniority Tone:** {st.session_state['ad_seniority_tone']}")
    st.markdown(f"**Ad Length Preference:** {st.session_state['ad_length_preference']}")
    st.markdown(f"**Deadline Urgency:** {st.session_state['deadline_urgency']}")
    st.markdown(f"**Company Awards:** {st.session_state['company_awards']}")
    st.markdown(f"**Diversity & Inclusion Statement:** {st.session_state['diversity_inclusion_statement']}")
    st.markdown(f"**Legal Disclaimers:** {st.session_state['legal_disclaimers']}")
    st.markdown(f"**Social Media Links:** {st.session_state['social_media_links']}")
    st.markdown(f"**Video Introduction Option:** {st.session_state['video_introduction_option']}")
    st.markdown(f"**Comments (Internal):** {st.session_state['comments_internal']}")

    st.info("You can still go back to previous steps to make changes if needed, or finalize now.")


###############################################################################
# NAVIGATION + MAIN
###############################################################################
def next_step():
    st.session_state["wizard_step"] += 1

def prev_step():
    st.session_state["wizard_step"] -= 1

def main():
    st.set_page_config(page_title="Vacancy Wizard", layout="wide")
    initialize_session_state()

    step = st.session_state["wizard_step"]

    if step == 1:
        start_discovery_page()        # NEW Step 1
    elif step == 2:
        render_step_2()              # Old Step 1 becomes Step 2
    elif step == 3:
        render_step_3()              # Old Step 2 becomes Step 3
    elif step == 4:
        render_step_4()              # Old Step 3 -> Step 4
    elif step == 5:
        render_step_5()              # Old Step 4 -> Step 5
    elif step == 6:
        render_step_6()              # Old Step 5 -> Step 6
    elif step == 7:
        render_step_7()              # Old Step 6 -> Step 7
    elif step == 8:
        render_step_8()              # Old Step 7 -> Step 8
    else:
        # If step out of range, fix to 1 or 8
        if step < 1:
            st.session_state["wizard_step"] = 1
            st.experimental_rerun()
        else:
            st.session_state["wizard_step"] = 8
            st.experimental_rerun()

    # If you still want Next/Back at bottom of each page:
    if step > 1:
        if st.button("⬅️ Back"):
            prev_step()
            st.experimental_rerun()
    if step < 8:
        if st.button("Next ➡"):
            next_step()
            st.experimental_rerun()

if __name__ == "__main__":
    main()

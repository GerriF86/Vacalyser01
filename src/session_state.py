import streamlit as st

# List of all session state keys for the wizard
SESSION_KEYS = [
    "job_title", "company_name", "brand_name", "headquarters_location", "company_website",
    "date_of_employment_start", "job_type", "contract_type", "job_level", "city",
    "team_structure", "role_description", "reports_to", "supervises", "role_type",
    "role_priority_projects", "travel_requirements", "work_schedule", "role_keywords",
    "decision_making_authority", "role_performance_metrics", "task_list", "key_responsibilities",
    "technical_tasks", "managerial_tasks", "administrative_tasks", "customer_facing_tasks",
    "internal_reporting_tasks", "performance_tasks", "innovation_tasks", "task_prioritization",
    "hard_skills", "soft_skills", "must_have_skills", "nice_to_have_skills", "certifications_required",
    "language_requirements", "tool_proficiency", "domain_expertise", "leadership_competencies",
    "technical_stack", "industry_experience", "analytical_skills", "communication_skills",
    "project_management_skills", "soft_requirement_details", "visa_sponsorship", "salary_range",
    "currency", "pay_frequency", "commission_structure", "bonus_scheme", "vacation_days",
    "flexible_hours", "remote_work_policy", "relocation_assistance", "childcare_support",
    "recruitment_steps", "recruitment_timeline", "number_of_interviews", "interview_format",
    "assessment_tests", "onboarding_process_overview", "recruitment_contact_email", "recruitment_contact_phone",
    "application_instructions", "parsed_data_raw", "language_of_ad", "translation_required",
    "employer_branding_elements", "desired_publication_channels", "internal_job_id", "ad_seniority_tone",
    "ad_length_preference", "deadline_urgency", "company_awards", "diversity_inclusion_statement",
    "legal_disclaimers", "social_media_links", "video_introduction_option", "comments_internal"
]

def initialize_session_state():
    """Initialize all required session state keys with default values (empty or sensible default)."""
    for key in SESSION_KEYS:
        if key not in st.session_state:
            # Set defaults for select fields, otherwise empty string
            if key == "role_type":
                st.session_state[key] = "Individual Contributor"
            elif key in ["visa_sponsorship", "flexible_hours", "relocation_assistance", "childcare_support", "translation_required", "video_introduction_option"]:
                st.session_state[key] = "No"
            elif key == "remote_work_policy":
                st.session_state[key] = "On-site"
            elif key == "ad_seniority_tone":
                st.session_state[key] = "Casual"
            elif key == "ad_length_preference":
                st.session_state[key] = "Short & Concise"
            elif key == "currency":
                st.session_state[key] = "EUR"
            elif key == "pay_frequency":
                st.session_state[key] = "Annual"
            elif key == "job_type":
                st.session_state[key] = "Full-time"
            elif key == "contract_type":
                st.session_state[key] = "Permanent"
            elif key == "job_level":
                st.session_state[key] = "Mid"
            else:
                st.session_state[key] = ""
    # Additional state keys not in SESSION_KEYS
    if "wizard_step" not in st.session_state:
        st.session_state["wizard_step"] = 1
    if "input_url" not in st.session_state:
        st.session_state["input_url"] = ""
    if "uploaded_file" not in st.session_state:
        st.session_state["uploaded_file"] = ""
    if "generated_job_ad" not in st.session_state:
        st.session_state["generated_job_ad"] = ""
    if "generated_prep" not in st.session_state:
        st.session_state["generated_prep"] = ""
    if "generated_contract" not in st.session_state:
        st.session_state["generated_contract"] = ""

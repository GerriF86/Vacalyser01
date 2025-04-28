#session_state.py

from __future__ import annotations
import streamlit as st

# All wizard inputs – *and* run-time generated artefacts –
# are defined in one flat list so they’re created exactly once.
_SESSION_KEYS: list[str] = [
    # ───── Static data gathered in the wizard ──────
    # Basic
    "job_title", "company_name", "brand_name", "headquarters_location",
    "company_website", "date_of_employment_start", "job_type",
    "contract_type", "job_level", "city", "team_structure",

    # Role definition
    "role_description", "reports_to", "supervises", "role_type",
    "role_priority_projects", "travel_requirements", "work_schedule",
    "role_keywords", "decision_making_authority", "role_performance_metrics",

    # Tasks & responsibilities
    "task_list", "key_responsibilities", "technical_tasks", "managerial_tasks",
    "administrative_tasks", "customer_facing_tasks", "internal_reporting_tasks",
    "performance_tasks", "innovation_tasks", "task_prioritization",

    # Skills & competencies
    "hard_skills", "soft_skills", "must_have_skills", "nice_to_have_skills",
    "certifications_required", "language_requirements", "tool_proficiency",
    "domain_expertise", "leadership_competencies", "technical_stack",
    "industry_experience", "analytical_skills", "communication_skills",
    "project_management_skills", "soft_requirement_details", "visa_sponsorship",

    # Compensation & benefits
    "salary_range", "currency", "pay_frequency", "commission_structure",
    "bonus_scheme", "vacation_days", "flexible_hours", "remote_work_policy",
    "relocation_assistance", "childcare_support",

    # Recruitment process
    "recruitment_steps", "recruitment_timeline", "number_of_interviews",
    "interview_format", "assessment_tests", "onboarding_process_overview",
    "recruitment_contact_email", "recruitment_contact_phone",
    "application_instructions",

    # Additional metadata
    "parsed_data_raw", "language_of_ad", "translation_required",
    "employer_branding_elements", "desired_publication_channels",
    "internal_job_id", "ad_seniority_tone", "ad_length_preference",
    "deadline_urgency", "company_awards", "diversity_inclusion_statement",
    "legal_disclaimers", "social_media_links", "video_introduction_option",
    "comments_internal",

    # ───── Runtime-generated artefacts ──────
    "target_group_analysis",        # LLM output
    "generated_job_ad",
    "generated_interview_prep",
    "generated_email_template",
    "generated_boolean_query",

    # Non-UI book-keeping
    "input_url",                    # URL entered on step 1
    "uploaded_file",                # raw text of uploaded file
    "wizard_step",                  # keeps track of current page
]

def initialize_session_state() -> None:
    """
    Ensure every expected key exists in st.session_state.

    Running this once at app start means every page can safely read
    and assign without defensive checks.
    """
    for key in _SESSION_KEYS:
        if key not in st.session_state:
            st.session_state[key] = ""

    # Start wizard on step 1 unless already set
    st.session_state.setdefault("wizard_step", 1)

# Expose list so other modules (e.g. extraction) know the canonical keys
SESSION_KEYS: tuple[str, ...] = tuple(_SESSION_KEYS)

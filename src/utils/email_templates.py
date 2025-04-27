# src/utils/email_templates.py
from string import Template

# Define example templates with placeholders
TEMPLATES = {
    "Candidate Outreach": (
        "Subject: Exciting Opportunity: $JOB_TITLE at $COMPANY\n\n"
        "Hi $FIRST_NAME,\n\n"
        "I came across your profile and thought you might be a great fit for our $JOB_TITLE role at $COMPANY. "
        "Given your experience with $SKILL and interest in $INDUSTRY, we'd love to discuss this opportunity with you.\n\n"
        "Would you be available for a quick chat?\n\nBest regards,\nHR Team"
    ),
    "Interview Invitation": (
        "Subject: Interview Invitation for $JOB_TITLE\n\n"
        "Dear $FIRST_NAME,\n\n"
        "Thank you for applying to $COMPANY for the position of $JOB_TITLE. "
        "We would like to invite you to an interview on $DATE. "
        "Please let us know if this time works for you.\n\n"
        "Best,\nRecruitment Team"
    )
}

def render_template(template_name: str, context: dict) -> str:
    """
    Fill in the selected template with values from context.
    """
    if template_name not in TEMPLATES:
        return ""
    tmpl_str = TEMPLATES[template_name]
    template = Template(tmpl_str)
    return template.safe_substitute(context)

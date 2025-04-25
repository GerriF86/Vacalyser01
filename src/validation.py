def validate_salary_input(salary_input: str) -> bool:
    """
    Example validation function for a salary range format.
    """
    if not salary_input.strip():
        # If empty, treat as valid
        return True
    parts = salary_input.replace(",", "").split("-")
    try:
        for part in parts:
            float(part.strip())
        return True
    except ValueError:
        return False

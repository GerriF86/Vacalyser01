#preprocessing.py

def clean_text(text: str) -> str:
    """
    Example text cleaning: remove extra whitespaces, fix encodings, etc.
    """
    text = text.replace("\r", " ").replace("\n", " ")
    text = " ".join(text.split())
    return text

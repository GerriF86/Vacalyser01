import requests
from bs4 import BeautifulSoup

def scrape_company_website(url: str) -> dict:
    """
    Fetch and parse a company or job ad webpage for basic info.
    Returns a dictionary with 'title' and 'description' if found.
    """
    result = {}
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception:
        return result
    soup = BeautifulSoup(resp.text, "html.parser")
    if soup.title and soup.title.string:
        result["title"] = soup.title.string.strip()
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        result["description"] = meta_desc["content"].strip()
    return result

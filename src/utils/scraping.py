import requests
from bs4 import BeautifulSoup

def scrape_company_website(url: str) -> dict:
    """
    Fetch and parse a company's website for basic info like title and meta description.
    Return a dict of extracted fields.
    """
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string if soup.title else "No Title Found"
        meta_desc_tag = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta_desc_tag["content"] if meta_desc_tag else "No Description Found"
        return {"title": title, "description": meta_desc}
    except Exception:
        return {}

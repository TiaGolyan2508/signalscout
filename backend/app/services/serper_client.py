import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
SERPER_URL = "https://google.serper.dev/search"

def search_companies(query: str, num_results: int = 10):
    """
    Search Google (via Serper) for companies matching a query.
    Returns a list of raw search results.
    """
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "q": query,
        "num": num_results
    }

    response = requests.post(SERPER_URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    results = []
    for item in data.get("organic", []):
        results.append({
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet")
        })

    return results
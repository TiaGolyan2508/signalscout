import os
import requests
from dotenv import load_dotenv

load_dotenv()

HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")
HUNTER_DOMAIN_SEARCH_URL = "https://api.hunter.io/v2/domain-search"

def find_contacts(domain: str, num_results: int = 10):
    """
    Given a company domain, find real emails + names + titles at that company.
    """
    params = {
        "domain": domain,
        "api_key": HUNTER_API_KEY,
        "limit": num_results
    }

    response = requests.get(HUNTER_DOMAIN_SEARCH_URL, params=params)
    response.raise_for_status()
    data = response.json()

    contacts = []
    for person in data.get("data", {}).get("emails", []):
        contacts.append({
            "first_name": person.get("first_name"),
            "last_name": person.get("last_name"),
            "email": person.get("value"),
            "title": person.get("position"),
            "confidence": person.get("confidence"),
            "linkedin_url": person.get("linkedin")
        })

    return contacts
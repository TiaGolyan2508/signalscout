from fastapi import APIRouter
from app.services.hunter_client import find_contacts

router = APIRouter()

@router.get("/enrich")
def enrich(domain: str, num_results: int = 10):
    contacts = find_contacts(domain, num_results)
    return {"domain": domain, "contacts": contacts}
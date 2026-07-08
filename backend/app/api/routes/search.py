from fastapi import APIRouter
from app.services.serper_client import search_companies

router = APIRouter()

@router.get("/search")
def search(query: str, num_results: int = 10):
    results = search_companies(query, num_results)
    return {"query": query, "results": results}
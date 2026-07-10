from fastapi import APIRouter
from app.agents.graph import run_pipeline

router = APIRouter()

@router.get("/pipeline")
def run(query: str):
    leads = run_pipeline(query)
    return {"query": query, "leads": leads}
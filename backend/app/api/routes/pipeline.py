from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.agents.graph import run_pipeline
from app.db.database import get_db
from app.services.db_service import save_leads

router = APIRouter()

@router.get("/pipeline")
def run(query: str, db: Session = Depends(get_db)):
    leads = run_pipeline(query)
    save_leads(db, query, leads)
    return {"query": query, "leads": leads}

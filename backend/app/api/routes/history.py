from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.db_service import get_all_leads

router = APIRouter()

@router.get("/history")
def history(db: Session = Depends(get_db)):
    records = get_all_leads(db)
    return {
        "leads": [
            {
                "id": r.id,
                "query": r.query,
                "company_name": r.company_name,
                "domain": r.domain,
                "snippet": r.snippet,
                "score": r.score,
                "score_reasoning": r.score_reasoning,
                "contacts": r.contacts,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in records
        ]
    }

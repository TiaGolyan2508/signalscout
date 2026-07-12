from sqlalchemy.orm import Session
from app.models.db_models import LeadRecord


def save_leads(db: Session, query: str, leads: list):
    """Save a batch of leads from a pipeline run into the database."""
    saved = []
    for lead in leads:
        record = LeadRecord(
            query=query,
            company_name=lead.get("company_name"),
            domain=lead.get("domain"),
            snippet=lead.get("snippet"),
            score=lead.get("score"),
            score_reasoning=lead.get("score_reasoning"),
            contacts=lead.get("contacts", [])
        )
        db.add(record)
        saved.append(record)
    db.commit()
    for record in saved:
        db.refresh(record)
    return saved


def get_all_leads(db: Session, limit: int = 50):
    """Fetch most recent saved leads."""
    return (
        db.query(LeadRecord)
        .order_by(LeadRecord.created_at.desc())
        .limit(limit)
        .all()
    )
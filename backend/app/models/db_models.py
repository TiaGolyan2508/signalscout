from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.db.database import Base


class LeadRecord(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, index=True)
    company_name = Column(String)
    domain = Column(String, index=True)
    snippet = Column(Text)
    score = Column(Float)
    score_reasoning = Column(Text)
    contacts = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

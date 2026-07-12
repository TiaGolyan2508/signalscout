from app.db.database import engine, Base
from app.models.db_models import LeadRecord

Base.metadata.create_all(bind=engine)
print("Tables created successfully.")

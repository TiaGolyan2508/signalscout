from fastapi import FastAPI
from app.api.routes import search, enrich, pipeline

app = FastAPI(title="SignalScout API")

app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(enrich.router, prefix="/api", tags=["enrich"])
app.include_router(pipeline.router, prefix="/api", tags=["pipeline"])

@app.get("/")
def root():
    return {"status": "ok", "message": "SignalScout API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
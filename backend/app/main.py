from fastapi import FastAPI
from app.api.routes import search

app = FastAPI(title="SignalScout API")

app.include_router(search.router, prefix="/api", tags=["search"])

@app.get("/")
def root():
    return {"status": "ok", "message": "SignalScout API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
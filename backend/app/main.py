from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import search, enrich, pipeline

app = FastAPI(title="SignalScout API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(enrich.router, prefix="/api", tags=["enrich"])
app.include_router(pipeline.router, prefix="/api", tags=["pipeline"])

@app.get("/")
def root():
    return {"status": "ok", "message": "SignalScout API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

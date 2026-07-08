from fastapi import FastAPI

app = FastAPI(title="SignalScout API")

@app.get("/")
def root():
    return {"status": "ok", "message": "SignalScout API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
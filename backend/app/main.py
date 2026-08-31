from fastapi import FastAPI

app = FastAPI(
    title="SentinelL402 API",
    description="Metered AI Cybersecurity Intelligence Agent",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SentinelL402 API",
        "version": "0.1.0",
    }

from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Indian Companies RAG API",
    description="Indian Companies Intelligence API",
    version="1.0.0"
)


# Register API routes
app.include_router(
    router,
    prefix="/api",
    tags=["Company Intelligence"]
)


@app.get("/")
def home():
    return {
        "message": "Indian Companies API is running"
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy"
    }

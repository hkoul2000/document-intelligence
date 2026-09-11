from fastapi import FastAPI

from app.api.routes.documents import router as documents_router
from app.core.database import Base, engine
from app.models.models import Document


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Document Intelligence API",
    description="AI-powered document extraction and financial validation API",
    version="1.0.0",
)


app.include_router(documents_router)


@app.get("/")
def root():
    return {
        "message": "Document Intelligence API is running"
    }


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "service": "document-intelligence-api",
    }
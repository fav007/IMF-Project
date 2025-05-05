from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import document_router
from .database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Document Management API",
    description="API for managing documents with deduplication support",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(document_router.router, prefix="/api/documents", tags=["documents"])

@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Document Management API is running"} 
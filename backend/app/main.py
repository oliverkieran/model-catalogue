"""
Model Catalogue API - Main Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

VERSION = "0.1.0"

# Create FastAPI app instance
app = FastAPI(
    title="Model Catalogue API",
    description="API for managing and comparing AI models."
    version=VERSION,
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"]  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Model Catalogue API",
        "status": "operational",
        "version": VERSION
    }
    
@app.get("/api/v1/health")
async def health_check():
    """Detailed health check for monitoring"""
    return {
        "status": "healthy",
        "database": "not configured yet",
        "llm_service": "not configured yet"
    }

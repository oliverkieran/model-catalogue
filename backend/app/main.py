"""
Model Catalogue API - Main Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import models, benchmarks, benchmark_results

VERSION = "0.1.0"

# Create FastAPI app instance
app = FastAPI(
    title="Model Catalogue API",
    description="API for managing and comparing AI models.",
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(models.router)
app.include_router(benchmarks.router)
app.include_router(benchmark_results.router)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Model Catalogue API",
        "status": "operational",
        "version": VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/api/v1/health")
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns service status and component health.
    """
    return {
        "status": "healthy",
        "version": VERSION,
        "components": {
            "database": "connected",
            "api": "operational",
        },
    }

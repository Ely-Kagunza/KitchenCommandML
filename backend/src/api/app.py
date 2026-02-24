"""
Main FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from datetime import datetime

from src.api.middleware import (
    AuthMiddleware,
    LoggingMiddleware,
    ErrorHandlingMiddleware,
    RateLimitMiddleware
)
from src.api.routes import health, predictions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Restaurant ML Service API",
    description="ML predictions for restaurant management system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
api_keys = os.getenv("API_KEYS", "").split(",")
app.add_middleware(AuthMiddleware, api_keys=api_keys)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=1000)

# Include routers
app.include_router(health.router)
app.include_router(predictions.router)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    logger.info("ML Service API starting up...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    logger.info("ML Service API shutting down...")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Restaurant ML Service API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/")
async def api_info():
    """API root endpoint."""
    return {
        "service": "Restaurant ML Service API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "predictions": "/api/predictions",
            "models": "/api/models"
        },
        "documentation": "/api/docs"
    }
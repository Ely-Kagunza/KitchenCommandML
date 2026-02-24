"""
Application entry point.
"""

import os
import sys
import logging
from config.settings import settings
from config.logging import setup_logging

# Setup logging
logger = setup_logging()

# Validate settings
try:
    settings.validate()
    logger.info("Settings validated successfully")
except ValueError as e:
    logger.error(f"Settings validation failed: {e}")
    sys.exit(1)

# Import FastAPI app
from src.api.app import app

if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting ML Service API on {settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")

    uvicorn.run(
        "src.api.app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS if not settings.DEBUG else 1,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

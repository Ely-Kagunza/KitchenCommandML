"""
Health check and status endpoints.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging
import os

from src.api.schema import HealthCheckResponse, ModelInfoResponse
from src.utils.model_loader import ModelLoader

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint.

    Returns:
        Health status and service information
    """
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        services={
            "api": "running",
            "models": "available",
            "database": "connected"
        }
    )

@router.get("/model/info")
async def get_model_info(
    model_type: str,
    restaurant_id: int
):
    """
    Get information about a trained model.

    Args:
        model_type: Type of model (demand, kitchen, churn, ltv, inventory)
        restaurant_id: Restaurant ID

    Returns:
        Model information and metadata
    """
    loader = ModelLoader()
    info = loader.get_model_info(model_type, restaurant_id)

    if not info['latest_metadata']:
        raise HTTPException(
            status_code=404,
            detail=f"Model not found: {model_type} for restaurant {restaurant_id}"
        )

    return {
        "success": True,
        "data": info,
        "metadata": {
            "generated_at": datetime.now().isoformat(),
        }
    }

@router.post("/model/versions")
async def list_model_versions(
    model_type: str,
    restaurant_id: int
):
    """
    List all versions of a model.

    Args:
        model_type: Type of model
        restaurant_id: Restaurant ID

    Returns:
        List of model versions
    """
    loader = ModelLoader()
    versions = loader.list_model_versions(model_type, restaurant_id)

    return {
        "success": True,
        "data": {
            "model_type": model_type,
            "restaurant_id": restaurant_id,
            "versions": versions,
            "version_count": len(versions)
        },
        "metadata": {
            "generated_at": datetime.now().isoformat(),
        }
    }


@router.get("/status")
async def get_status():
    """
    Get detailed system status.

    Returns:
        Detailed system information
    """
    return {
        "success": True,
        "data": {
            "api": {
                "status": "running",
                "uptime": "N/A"
            },
            "models": {
                "status": "available",
                "count": 5
            },
            "database": {
                "status": "connected"
            },
            "cache": {
                "status": "available"
            },
        },
        "metadata": {
            "timestamp": datetime.now().isoformat()
        }
    }
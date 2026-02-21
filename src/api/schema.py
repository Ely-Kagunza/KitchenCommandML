"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime


# Request Schemas

class DemandForecastRequest(BaseModel):
    """Request for demand forecast."""
    restaurant_id: Union[int, str] = Field(..., description="Restaurant ID (UUID or integer)")
    hours_ahead: int = Field(default=24, ge=1, le=168)
    forecast_type: str = Field(default="hourly", pattern='^(hourly|daily)$')
    
    @field_validator('restaurant_id', mode='before')
    @classmethod
    def convert_restaurant_id(cls, v):
        """Convert restaurant_id to string (UUID format)."""
        if isinstance(v, int):
            return str(v)
        return str(v)


class KitchenPredictionRequest(BaseModel):
    """Request for kitchen prediction."""
    restaurant_id: Union[int, str] = Field(..., description="Restaurant ID (UUID or integer)")
    station_id: int = Field(..., gt=0)
    menu_item_id: int = Field(..., gt=0)
    
    @field_validator('restaurant_id', mode='before')
    @classmethod
    def convert_restaurant_id(cls, v):
        """Convert restaurant_id to string (UUID format)."""
        if isinstance(v, int):
            return str(v)
        return str(v)


class CustomerAnalyticsRequest(BaseModel):
    """Request for customer analytics."""
    restaurant_id: Union[int, str] = Field(..., description="Restaurant ID (UUID or integer)")
    customer_id: int = Field(..., gt=0)
    
    @field_validator('restaurant_id', mode='before')
    @classmethod
    def convert_restaurant_id(cls, v):
        """Convert restaurant_id to string (UUID format)."""
        if isinstance(v, int):
            return str(v)
        return str(v)


class InventoryOptimizationRequest(BaseModel):
    """Request for inventory optimization."""
    restaurant_id: Union[int, str] = Field(..., description="Restaurant ID (UUID or integer)")
    item_id: int = Field(..., gt=0)
    
    @field_validator('restaurant_id', mode='before')
    @classmethod
    def convert_restaurant_id(cls, v):
        """Convert restaurant_id to string (UUID format)."""
        if isinstance(v, int):
            return str(v)
        return str(v)


# Response Schemas

class PredictionMetadata(BaseModel):
    """Metadata for predictions."""
    model_version: str
    prediction_time_ms: float
    cached: bool = False
    generated_at: str


class SuccessResponse(BaseModel):
    """Generic success response."""
    success: bool = True
    data: Dict[str, Any]
    metadata: PredictionMetadata


class ErrorResponse(BaseModel):
    """Generic error response."""
    success: bool = False
    error: str
    message: str
    timestamp: str


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    version: str
    services: Dict[str, str]


class ModelInfoResponse(BaseModel):
    """Model information response."""
    model_type: str
    restaurant_id: Union[int, str]
    version: str
    trained_at: str
    metrics: Dict[str, float]
    feature_count: Optional[int] = None


class DemandPredictionResponse(BaseModel):
    """Demand prediction response."""
    forecast_type: str
    hours_ahead: Optional[int] = None
    days_ahead: Optional[int] = None
    predictions: List[Dict[str, Any]]
    generated_at: str


class KitchenPredictionResponse(BaseModel):
    """Kitchen prediction response."""
    station_id: int
    menu_item_id: int
    predicted_prep_time_minutes: float
    lower_bound_minutes: float
    upper_bound_minutes: float
    confidence: float


class CustomerAnalyticsResponse(BaseModel):
    """Customer analytics response."""
    customer_id: int
    churn_probability: float
    churn_risk_segment: str
    predicted_ltv: float
    ltv_segment: str
    recommendations: List[str]


class InventoryRecommendationResponse(BaseModel):
    """Inventory recommendation response."""
    item_id: int
    current_stock: float
    action: str
    urgency: str
    reason: str
    recommended_order_qty: float
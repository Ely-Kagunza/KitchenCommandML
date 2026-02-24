"""
Prediction endpoints for all ML models.
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import logging
import time
import pandas as pd
import os
from typing import Union

from src.api.schema import (
    DemandForecastRequest,
    KitchenPredictionRequest,
    CustomerAnalyticsRequest,
    InventoryOptimizationRequest,
    SuccessResponse,
    PredictionMetadata
)
from src.services import (
    DemandPredictionService,
    KitchenPredictionService,
    CustomerPredictionService,
    InventoryPredictionService
)
from src.pipelines.data_extractor import RMSDataExtractor
from src.utils.model_loader import ModelLoader

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/predictions", tags=["predictions"])

# Lazy initialization - will be created on first use
_data_extractor = None
_model_loader = None


def get_data_extractor():
    """Get or create data extractor instance."""
    global _data_extractor
    if _data_extractor is None:
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            raise RuntimeError("DATABASE_URL environment variable not set")
        _data_extractor = RMSDataExtractor(db_url)
    return _data_extractor


def get_model_loader():
    """Get or create model loader instance."""
    global _model_loader
    if _model_loader is None:
        _model_loader = ModelLoader()
    return _model_loader


def normalize_restaurant_id(restaurant_id: Union[int, str]) -> str:
    """Convert restaurant_id to string format."""
    return str(restaurant_id)


@router.post("/demand")
async def predict_demand(request: DemandForecastRequest):
    """
    Predict demand for next N hours/days.

    Args:
        request: Demand forecast request

    Returns:
        Demand predictions
    """
    start_time = time.time()
    
    # Normalize restaurant_id
    restaurant_id = normalize_restaurant_id(request.restaurant_id)

    try:
        # Get model path
        model_path = get_model_loader().get_latest_model_path('demand', restaurant_id)
        if not model_path:
            raise HTTPException(
                status_code=404,
                detail=f"No demand model found for restaurant {restaurant_id}"
            )

        # Initialize service
        service = DemandPredictionService(model_path)

        # Get historical data
        end_date = datetime.now()
        start_date = end_date - pd.Timedelta(days=180)

        orders = get_data_extractor().extract_orders(
            restaurant_id,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

        # Generate predictions
        if request.forecast_type == 'hourly':
            predictions = service.predict_hourly(orders, request.hours_ahead)
        else:
            predictions = service.predict_daily(orders, request.hours_ahead)

        duration = (time.time() - start_time) * 1000

        return {
            "success": True,
            "data": predictions,
            "metadata": {
                "model_version": "1.0.0",
                "prediction_time_ms": round(duration, 2),
                "cached": False,
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error predicting demand: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/demand/items")
async def predict_item_demand(
    restaurant_id: Union[int, str],
    item_id: int,
    hours_ahead: int = 24
):
    """
    Predict demand for a specific menu item.

    Args:
        restaurant_id: Restaurant ID
        item_id: Menu item ID
        hours_ahead: Hours to forecast

    Returns:
        Item-level demand predictions
    """
    start_time = time.time()
    
    # Normalize restaurant_id
    restaurant_id = normalize_restaurant_id(restaurant_id)

    try:
        model_path = get_model_loader().get_latest_model_path('demand', restaurant_id)
        if not model_path:
            raise HTTPException(status_code=404, detail="Model not found")

        service = DemandPredictionService(model_path)

        end_date = datetime.now()
        start_date = end_date - pd.Timedelta(days=180)

        orders = get_data_extractor().extract_orders(
            restaurant_id,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

        predictions = service.predict_item_demand(orders, item_id, hours_ahead)

        duration = (time.time() - start_time) * 1000

        return {
            "success": True,
            "data": predictions,
            "metadata": {
                "model_version": "1.0.0",
                "prediction_time_ms": round(duration, 2),
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error predicting item demand: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/demand/category")
async def predict_category_demand(
    restaurant_id: Union[int, str],
    category_name: str,
    hours_ahead: int = 24
):
    """
    Predict demand for a menu category.

    Args:
        restaurant_id: Restaurant ID
        category_name: Menu category name
        hours_ahead: Hours to forecast

    Returns:
        Category-level demand predictions
    """
    start_time = time.time()
    
    # Normalize restaurant_id
    restaurant_id = normalize_restaurant_id(restaurant_id)

    try:
        model_path = get_model_loader().get_latest_model_path('demand', restaurant_id)
        if not model_path:
            raise HTTPException(status_code=404, detail="Model not found")

        service = DemandPredictionService(model_path)

        end_date = datetime.now()
        start_date = end_date - pd.Timedelta(days=180)

        orders = get_data_extractor().extract_orders(
            restaurant_id,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

        predictions = service.predict_category_demand(orders, category_name, hours_ahead)

        duration = (time.time() - start_time) * 1000

        return {
            "success": True,
            "data": predictions,
            "metadata": {
                "model_version": "1.0.0",
                "prediction_time_ms": round(duration, 2),
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error predicting category demand: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/demand/peak-hours")
async def get_peak_hours(
    restaurant_id: Union[int, str],
    days_ahead: int = 7
):
    """
    Get peak hours forecast for next N days.

    Args:
        restaurant_id: Restaurant ID
        days_ahead: Days to forecast

    Returns:
        Peak hours analysis
    """
    start_time = time.time()
    
    # Normalize restaurant_id
    restaurant_id = normalize_restaurant_id(restaurant_id)

    try:
        model_path = get_model_loader().get_latest_model_path('demand', restaurant_id)
        if not model_path:
            raise HTTPException(status_code=404, detail="Model not found")

        service = DemandPredictionService(model_path)

        end_date = datetime.now()
        start_date = end_date - pd.Timedelta(days=180)

        orders = get_data_extractor().extract_orders(
            restaurant_id,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

        analysis = service.get_peak_hours(orders, days_ahead)

        duration = (time.time() - start_time) * 1000

        return {
            "success": True,
            "data": analysis,
            "metadata": {
                "prediction_time_ms": round(duration, 2),
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error getting peak hours: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kitchen/prep-time")
async def predict_prep_time(request: KitchenPredictionRequest):
    """
    Predict kitchen prep time for item at station.

    Args:
        request: Kitchen prediction request

    Returns:
        Prep time prediction with confidence interval
    """
    start_time = time.time()
    
    # Normalize restaurant_id
    restaurant_id = normalize_restaurant_id(request.restaurant_id)

    try:
        model_path = get_model_loader().get_latest_model_path('kitchen', restaurant_id)
        if not model_path:
            raise HTTPException(status_code=404, detail="Model not found")

        service = KitchenPredictionService(model_path)

        end_date = datetime.now()
        start_date = end_date - pd.Timedelta(days=90)

        kitchen_data = get_data_extractor().extract_kitchen_performance(
            restaurant_id,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

        prediction = service.predict_prep_time(
            request.station_id,
            request.menu_item_id,
            kitchen_data
        )

        duration = (time.time() - start_time) * 1000

        return {
            "success": True,
            "data": prediction,
            "metadata": {
                "model_version": "1.0.0",
                "prediction_time_ms": round(duration, 2),
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error predicting prep time: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kitchen/batch-prep-time")
async def predict_batch_prep_time(request: KitchenPredictionRequest):
    """
    Predict prep times for batch of orders.

    Args:
        request: Kitchen prediction request with orders list

    Returns:
        Batch prep time predictions
    """
    start_time = time.time()
    
    # Normalize restaurant_id
    restaurant_id = normalize_restaurant_id(request.restaurant_id)

    try:
        model_path = get_model_loader().get_latest_model_path('kitchen', restaurant_id)
        if not model_path:
            raise HTTPException(status_code=404, detail="Model not found")

        service = KitchenPredictionService(model_path)

        end_date = datetime.now()
        start_date = end_date - pd.Timedelta(days=90)

        kitchen_data = get_data_extractor().extract_kitchen_performance(
            restaurant_id,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

        # Assuming request has orders list
        orders = getattr(request, 'orders', [])
        if not orders:
            raise HTTPException(status_code=400, detail="Orders list required")

        prediction = service.predict_batch_prep_time(orders, kitchen_data)

        duration = (time.time() - start_time) * 1000

        return {
            "success": True,
            "data": prediction,
            "metadata": {
                "model_version": "1.0.0",
                "prediction_time_ms": round(duration, 2),
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error predicting batch prep time: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kitchen/bottlenecks")
async def identify_bottlenecks(restaurant_id: Union[int, str]):
    """
    Identify kitchen bottlenecks.

    Args:
        restaurant_id: Restaurant ID

    Returns:
        Bottleneck analysis
    """
    start_time = time.time()
    
    # Normalize restaurant_id
    restaurant_id = normalize_restaurant_id(restaurant_id)

    try:
        model_path = get_model_loader().get_latest_model_path('kitchen', restaurant_id)
        if not model_path:
            raise HTTPException(status_code=404, detail="Model not found")

        service = KitchenPredictionService(model_path)

        end_date = datetime.now()
        start_date = end_date - pd.Timedelta(days=30)

        kitchen_data = get_data_extractor().extract_kitchen_performance(
            restaurant_id,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

        analysis = service.identify_bottlenecks(kitchen_data)

        duration = (time.time() - start_time) * 1000

        return {
            "success": True,
            "data": analysis,
            "metadata": {
                "prediction_time_ms": round(duration, 2),
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error identifying bottlenecks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kitchen/station-performance")
async def get_station_performance(restaurant_id: Union[int, str]):
    """
    Get kitchen station performance metrics.

    Args:
        restaurant_id: Restaurant ID

    Returns:
        Station performance analysis
    """
    start_time = time.time()
    
    # Normalize restaurant_id
    restaurant_id = normalize_restaurant_id(restaurant_id)

    try:
        model_path = get_model_loader().get_latest_model_path('kitchen', restaurant_id)
        if not model_path:
            raise HTTPException(status_code=404, detail="Model not found")

        service = KitchenPredictionService(model_path)

        end_date = datetime.now()
        start_date = end_date - pd.Timedelta(days=30)

        kitchen_data = get_data_extractor().extract_kitchen_performance(
            restaurant_id,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

        analysis = service.get_station_performance(kitchen_data)

        duration = (time.time() - start_time) * 1000

        return {
            "success": True,
            "data": analysis,
            "metadata": {
                "prediction_time_ms": round(duration, 2),
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error getting station performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/customer/churn")
async def predict_churn(request: CustomerAnalyticsRequest):
    """
    Predict customer churn probability.

    Args:
        request: Customer analytics request

    Returns:
        Churn prediction with risk segments
    """
    start_time = time.time()
    
    # Normalize restaurant_id
    restaurant_id = normalize_restaurant_id(request.restaurant_id)

    try:
        churn_path = get_model_loader().get_latest_model_path('churn', restaurant_id)
        ltv_path = get_model_loader().get_latest_model_path('ltv', restaurant_id)

        if not churn_path or not ltv_path:
            raise HTTPException(status_code=404, detail="Model not found")

        service = CustomerPredictionService(churn_path, ltv_path)

        customers = get_data_extractor().extract_customer_data(restaurant_id)
        customer = customers[customers['customer_id'] == request.customer_id]

        if len(customer) == 0:
            raise HTTPException(status_code=404, detail="Customer not found")

        prediction = service.predict_churn(customer.iloc[0])

        duration = (time.time() - start_time) * 1000

        return {
            "success": True,
            "data": prediction,
            "metadata": {
                "model_version": "1.0.0",
                "prediction_time_ms": round(duration, 2),
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error predicting churn: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/customer/ltv")
async def predict_ltv(request: CustomerAnalyticsRequest):
    """
    Predict customer lifetime value.

    Args:
        request: Customer analytics request

    Returns:
        LTV prediction with segments
    """
    start_time = time.time()
    
    # Normalize restaurant_id
    restaurant_id = normalize_restaurant_id(request.restaurant_id)

    try:
        churn_path = get_model_loader().get_latest_model_path('churn', restaurant_id)
        ltv_path = get_model_loader().get_latest_model_path('ltv', restaurant_id)

        if not churn_path or not ltv_path:
            raise HTTPException(status_code=404, detail="Model not found")

        service = CustomerPredictionService(churn_path, ltv_path)

        customers = get_data_extractor().extract_customer_data(restaurant_id)
        customer = customers[customers['customer_id'] == request.customer_id]

        if len(customer) == 0:
            raise HTTPException(status_code=404, detail="Customer not found")

        prediction = service.predict_ltv(customer.iloc[0])

        duration = (time.time() - start_time) * 1000

        return {
            "success": True,
            "data": prediction,
            "metadata": {
                "model_version": "1.0.0",
                "prediction_time_ms": round(duration, 2),
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error predicting LTV: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/customer/batch-analytics")
async def predict_batch_analytics(restaurant_id: Union[int, str]):
    """
    Get analytics for all customers.

    Args:
        restaurant_id: Restaurant ID

    Returns:
        Batch customer analytics
    """
    start_time = time.time()
    
    # Normalize restaurant_id
    restaurant_id = normalize_restaurant_id(restaurant_id)

    try:
        churn_path = get_model_loader().get_latest_model_path('churn', restaurant_id)
        ltv_path = get_model_loader().get_latest_model_path('ltv', restaurant_id)

        if not churn_path or not ltv_path:
            raise HTTPException(status_code=404, detail="Model not found")

        service = CustomerPredictionService(churn_path, ltv_path)

        customers = get_data_extractor().extract_customer_data(restaurant_id)
        analysis = service.predict_batch_analytics(customers)

        duration = (time.time() - start_time) * 1000

        return {
            "success": True,
            "data": analysis,
            "metadata": {
                "prediction_time_ms": round(duration, 2),
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error getting batch analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customer/at-risk")
async def get_at_risk_customers(restaurant_id: Union[int, str], threshold: float = 0.6):
    """
    Get customers at risk of churn.

    Args:
        restaurant_id: Restaurant ID
        threshold: Churn probability threshold

    Returns:
        List of customers at risk
    """
    start_time = time.time()
    
    # Normalize restaurant_id
    restaurant_id = normalize_restaurant_id(restaurant_id)

    try:
        churn_path = get_model_loader().get_latest_model_path('churn', restaurant_id)
        ltv_path = get_model_loader().get_latest_model_path('ltv', restaurant_id)

        if not churn_path or not ltv_path:
            raise HTTPException(status_code=404, detail="Model not found")

        service = CustomerPredictionService(churn_path, ltv_path)

        customers = get_data_extractor().extract_customer_data(restaurant_id)
        analysis = service.get_at_risk_customers(customers, threshold)

        duration = (time.time() - start_time) * 1000

        return {
            "success": True,
            "data": analysis,
            "metadata": {
                "prediction_time_ms": round(duration, 2),
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error getting at risk customers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customer/high-value")
async def get_high_value_customers(restaurant_id: Union[int, str], ltv_percentile: float = 75):
    """
    Get high-value customers.

    Args:
        restaurant_id: Restaurant ID
        ltv_percentile: LTV percentile threshold

    Returns:
        List of high-value customers
    """
    start_time = time.time()
    
    # Normalize restaurant_id
    restaurant_id = normalize_restaurant_id(restaurant_id)

    try:
        churn_path = get_model_loader().get_latest_model_path('churn', restaurant_id)
        ltv_path = get_model_loader().get_latest_model_path('ltv', restaurant_id)

        if not churn_path or not ltv_path:
            raise HTTPException(status_code=404, detail="Model not found")

        service = CustomerPredictionService(churn_path, ltv_path)

        customers = get_data_extractor().extract_customer_data(restaurant_id)
        analysis = service.get_high_value_customers(customers, ltv_percentile)

        duration = (time.time() - start_time) * 1000

        return {
            "success": True,
            "data": analysis,
            "metadata": {
                "prediction_time_ms": round(duration, 2),
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error getting high value customers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inventory/recommendations")
async def get_inventory_recommendations(request: InventoryOptimizationRequest):
    """
    Get inventory recommendations for item.

    Args:
        request: Inventory optimization request

    Returns:
        Inventory recommendations
    """
    start_time = time.time()
    
    # Normalize restaurant_id
    restaurant_id = normalize_restaurant_id(request.restaurant_id)

    try:
        model_path = get_model_loader().get_latest_model_path('inventory', restaurant_id)
        if not model_path:
            raise HTTPException(status_code=404, detail="Model not found")

        service = InventoryPredictionService(model_path)

        inventory = get_data_extractor().extract_inventory_data(restaurant_id)
        item = inventory[inventory['item_id'] == request.item_id]

        if len(item) == 0:
            raise HTTPException(status_code=404, detail="Item not found")

        recommendation = service.get_item_recommendation(
            request.item_id,
            item.iloc[0]['current_stock'],
            item.iloc[0]['daily_consumption_rate'],
            item.iloc[0]['reorder_level'],
            item.iloc[0]['reorder_level'] * 2,
            item.iloc[0]['min_level']
        )

        duration = (time.time() - start_time) * 1000

        return {
            "success": True,
            "data": recommendation,
            "metadata": {
                "model_version": "1.0.0",
                "prediction_time_ms": round(duration, 2),
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error getting inventory recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inventory/batch-recommendations")
async def get_batch_inventory_recommendations(restaurant_id: Union[int, str]):
    """
    Get inventory recommendations for all items.

    Args:
        restaurant_id: Restaurant ID

    Returns:
        Batch inventory recommendations
    """
    start_time = time.time()
    
    # Normalize restaurant_id
    restaurant_id = normalize_restaurant_id(restaurant_id)

    try:
        model_path = get_model_loader().get_latest_model_path('inventory', restaurant_id)
        if not model_path:
            raise HTTPException(status_code=404, detail="Model not found")

        service = InventoryPredictionService(model_path)

        inventory = get_data_extractor().extract_inventory_data(restaurant_id)
        recommendations = service.get_batch_recommendations(inventory)

        duration = (time.time() - start_time) * 1000

        return {
            "success": True,
            "data": recommendations,
            "metadata": {
                "prediction_time_ms": round(duration, 2),
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error getting batch recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inventory/reorder-summary")
async def get_reorder_summary(restaurant_id: Union[int, str]):
    """
    Get summary of items needing reorder.

    Args:
        restaurant_id: Restaurant ID

    Returns:
        Reorder summary
    """
    start_time = time.time()
    
    # Normalize restaurant_id
    restaurant_id = normalize_restaurant_id(restaurant_id)

    try:
        model_path = get_model_loader().get_latest_model_path('inventory', restaurant_id)
        if not model_path:
            raise HTTPException(status_code=404, detail="Model not found")

        service = InventoryPredictionService(model_path)

        inventory = get_data_extractor().extract_inventory_data(restaurant_id)
        summary = service.get_reorder_summary(inventory)

        duration = (time.time() - start_time) * 1000

        return {
            "success": True,
            "data": summary,
            "metadata": {
                "prediction_time_ms": round(duration, 2),
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error getting reorder summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inventory/status")
async def get_inventory_status(restaurant_id: Union[int, str]):
    """
    Get overall inventory status report.

    Args:
        restaurant_id: Restaurant ID

    Returns:
        Inventory status report
    """
    start_time = time.time()
    
    # Normalize restaurant_id
    restaurant_id = normalize_restaurant_id(restaurant_id)

    try:
        model_path = get_model_loader().get_latest_model_path('inventory', restaurant_id)
        if not model_path:
            raise HTTPException(status_code=404, detail="Model not found")

        service = InventoryPredictionService(model_path)

        inventory = get_data_extractor().extract_inventory_data(restaurant_id)
        report = service.get_stock_status_report(inventory)

        duration = (time.time() - start_time) * 1000

        return {
            "success": True,
            "data": report,
            "metadata": {
                "prediction_time_ms": round(duration, 2),
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error getting inventory status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inventory/optimize")
async def optimize_inventory(restaurant_id: Union[int, str], item_id: int):
    """
    Get comprehensive inventory optimization for item.

    Args:
        restaurant_id: Restaurant ID
        item_id: Item ID

    Returns:
        Inventory optimization results
    """
    start_time = time.time()
    
    # Normalize restaurant_id
    restaurant_id = normalize_restaurant_id(restaurant_id)

    try:
        model_path = get_model_loader().get_latest_model_path('inventory', restaurant_id)
        if not model_path:
            raise HTTPException(status_code=404, detail="Model not found")

        service = InventoryPredictionService(model_path)

        inventory = get_data_extractor().extract_inventory_data(restaurant_id)
        item = inventory[inventory['item_id'] == item_id]

        if len(item) == 0:
            raise HTTPException(status_code=404, detail="Item not found")

        item_row = item.iloc[0]
        optimization = service.optimize_inventory(
            item_id,
            item_row['current_stock'],
            item_row['daily_consumption_rate'],
            lead_time_days=3,  # Default lead time
            order_cost=50,  # Default order cost
            holding_cost=0.5,  # Default holding cost
            min_level=item_row['min_level']
        )

        duration = (time.time() - start_time) * 1000

        return {
            "success": True,
            "data": optimization,
            "metadata": {
                "prediction_time_ms": round(duration, 2),
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error optimizing inventory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inventory/waste-insights")
async def get_waste_reduction_insights(restaurant_id: Union[int, str]):
    """
    Get waste reduction insights.

    Args:
        restaurant_id: Restaurant ID

    Returns:
        Waste reduction insights
    """
    start_time = time.time()
    
    # Normalize restaurant_id
    restaurant_id = normalize_restaurant_id(restaurant_id)

    try:
        model_path = get_model_loader().get_latest_model_path('inventory', restaurant_id)
        if not model_path:
            raise HTTPException(status_code=404, detail="Model not found")

        service = InventoryPredictionService(model_path)

        inventory = get_data_extractor().extract_inventory_data(restaurant_id)
        insights = service.get_waste_reduction_insights(inventory)

        duration = (time.time() - start_time) * 1000

        return {
            "success": True,
            "data": insights,
            "metadata": {
                "prediction_time_ms": round(duration, 2),
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error getting waste insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inventory/cost-analysis")
async def get_cost_analysis(restaurant_id: Union[int, str]):
    """
    Get inventory cost analysis.

    Args:
        restaurant_id: Restaurant ID

    Returns:
        Cost analysis report
    """
    start_time = time.time()
    
    # Normalize restaurant_id
    restaurant_id = normalize_restaurant_id(restaurant_id)

    try:
        model_path = get_model_loader().get_latest_model_path('inventory', restaurant_id)
        if not model_path:
            raise HTTPException(status_code=404, detail="Model not found")

        service = InventoryPredictionService(model_path)

        inventory = get_data_extractor().extract_inventory_data(restaurant_id)
        analysis = service.get_cost_analysis(inventory, order_cost=50)

        duration = (time.time() - start_time) * 1000

        return {
            "success": True,
            "data": analysis,
            "metadata": {
                "prediction_time_ms": round(duration, 2),
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error getting cost analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

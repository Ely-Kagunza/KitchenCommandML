# ML Service API Endpoints Documentation

## Overview

Complete REST API for all ML prediction services. All endpoints return standardized responses with success status, data, and metadata.

---

## Base URL

```
http://localhost:8000/api/predictions
```

---

## Response Format

All endpoints return responses in this format:

```json
{
  "success": true,
  "data": {
    /* prediction data */
  },
  "metadata": {
    "model_version": "1.0.0",
    "prediction_time_ms": 125.45,
    "generated_at": "2026-02-24T16:30:00.000000"
  }
}
```

---

## DEMAND FORECASTING ENDPOINTS

### 1. Predict Hourly/Daily Demand

**POST** `/demand`

Forecast demand for next N hours or days.

**Request Body:**

```json
{
  "restaurant_id": "a33877ad-36ac-420a-96d0-6f518e5af21b",
  "forecast_type": "hourly",
  "hours_ahead": 24
}
```

**Parameters:**

- `restaurant_id` (string, UUID): Restaurant identifier
- `forecast_type` (string): "hourly" or "daily"
- `hours_ahead` (integer): Hours to forecast (for hourly)
- `days_ahead` (integer): Days to forecast (for daily)

**Response:**

```json
{
  "success": true,
  "data": {
    "forecast_type": "hourly",
    "hours_ahead": 24,
    "predictions": [
      {
        "timestamp": "2026-02-24T17:00:00",
        "hour": 17,
        "predicted_orders": 3,
        "confidence": 0.85
      }
    ]
  }
}
```

---

### 2. Predict Item-Level Demand

**POST** `/demand/items`

Forecast demand for a specific menu item.

**Query Parameters:**

- `restaurant_id` (string, UUID): Restaurant identifier
- `item_id` (integer): Menu item ID
- `hours_ahead` (integer, default: 24): Hours to forecast

**Response:**

```json
{
  "success": true,
  "data": {
    "item_id": 1,
    "item_name": "Burger",
    "forecast_type": "item_hourly",
    "hours_ahead": 24,
    "predictions": [
      {
        "timestamp": "2026-02-24T17:00:00",
        "predicted_orders": 2
      }
    ]
  }
}
```

---

### 3. Predict Category-Level Demand

**POST** `/demand/category`

Forecast demand for a menu category.

**Query Parameters:**

- `restaurant_id` (string, UUID): Restaurant identifier
- `category_name` (string): Menu category name
- `hours_ahead` (integer, default: 24): Hours to forecast

**Response:**

```json
{
  "success": true,
  "data": {
    "category": "Burgers",
    "forecast_type": "category_hourly",
    "hours_ahead": 24,
    "predictions": [
      {
        "timestamp": "2026-02-24T17:00:00",
        "predicted_orders": 5
      }
    ]
  }
}
```

---

### 4. Get Peak Hours

**GET** `/demand/peak-hours`

Identify peak hours for next N days.

**Query Parameters:**

- `restaurant_id` (string, UUID): Restaurant identifier
- `days_ahead` (integer, default: 7): Days to analyze

**Response:**

```json
{
  "success": true,
  "data": {
    "analysis_type": "peak_hours",
    "days_ahead": 7,
    "analysis": [
      {
        "date": "2026-02-24",
        "peak_hours": [
          {
            "hour": 12,
            "predicted_orders": 15
          },
          {
            "hour": 18,
            "predicted_orders": 12
          }
        ]
      }
    ]
  }
}
```

---

## KITCHEN SERVICE ENDPOINTS

### 5. Predict Prep Time

**POST** `/kitchen/prep-time`

Predict preparation time for a menu item at a specific station.

**Request Body:**

```json
{
  "restaurant_id": "a33877ad-36ac-420a-96d0-6f518e5af21b",
  "station_id": 1,
  "menu_item_id": 5
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "station_id": 1,
    "menu_item_id": 5,
    "predicted_prep_time_minutes": 4.2,
    "lower_bound_minutes": 3.1,
    "upper_bound_minutes": 5.3,
    "confidence": 0.85
  }
}
```

---

### 6. Predict Batch Prep Time

**POST** `/kitchen/batch-prep-time`

Predict prep times for multiple orders.

**Request Body:**

```json
{
  "restaurant_id": "a33877ad-36ac-420a-96d0-6f518e5af21b",
  "orders": [
    {
      "station_id": 1,
      "menu_item_id": 5
    },
    {
      "station_id": 2,
      "menu_item_id": 8
    }
  ]
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "batch_size": 2,
    "item_predictions": [
      {
        "station_id": 1,
        "menu_item_id": 5,
        "predicted_prep_time_minutes": 4.2,
        "lower_bound_minutes": 3.1,
        "upper_bound_minutes": 5.3,
        "confidence": 0.85
      }
    ],
    "estimated_total_time_minutes": 6.5,
    "generated_at": "2026-02-24T16:30:00"
  }
}
```

---

### 7. Identify Kitchen Bottlenecks

**GET** `/kitchen/bottlenecks`

Identify slow-performing items and stations.

**Query Parameters:**

- `restaurant_id` (string, UUID): Restaurant identifier

**Response:**

```json
{
  "success": true,
  "data": {
    "analysis_type": "bottleneck_detection",
    "bottlenecks": [
      {
        "station_id": "1",
        "station_name": "Grill",
        "avg_prep_time": 1.3,
        "bottleneck_threshold": 2.5,
        "slow_items": [
          {
            "menu_item_id": 23,
            "avg_prep_time": 8.3,
            "occurences": 12
          }
        ]
      }
    ]
  }
}
```

---

### 8. Get Station Performance

**GET** `/kitchen/station-performance`

Get performance metrics for each kitchen station.

**Query Parameters:**

- `restaurant_id` (string, UUID): Restaurant identifier

**Response:**

```json
{
  "success": true,
  "data": {
    "analysis_type": "station_performance",
    "stations": [
      {
        "station_id": "1",
        "station_name": "Grill",
        "total_items_prepared": 92,
        "avg_prep_time_minutes": 1.3,
        "median_prep_time_minutes": 1.2,
        "std_dev_prep_time": 0.8,
        "min_prep_time": 0.5,
        "max_prep_time": 6.4,
        "within_5_min_accuracy": 89.1
      }
    ]
  }
}
```

---

## CUSTOMER ANALYTICS ENDPOINTS

### 9. Predict Customer Churn

**POST** `/customer/churn`

Predict probability of customer churn.

**Request Body:**

```json
{
  "restaurant_id": "a33877ad-36ac-420a-96d0-6f518e5af21b",
  "customer_id": 123
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "customer_id": 123,
    "churn_probability": 0.1192,
    "risk_segment": "low_risk",
    "will_churn": 0,
    "confidence": 0.85
  }
}
```

---

### 10. Predict Customer Lifetime Value

**GET** `/customer/ltv`

Predict customer lifetime value.

**Query Parameters:**

- `restaurant_id` (string, UUID): Restaurant identifier
- `customer_id` (integer): Customer ID

**Response:**

```json
{
  "success": true,
  "data": {
    "customer_id": 123,
    "predicted_ltv": 39588.89,
    "ltv_segment": "high_value",
    "confidence": 0.8
  }
}
```

---

### 11. Get Batch Customer Analytics

**POST** `/customer/batch-analytics`

Get churn and LTV predictions for all customers.

**Query Parameters:**

- `restaurant_id` (string, UUID): Restaurant identifier

**Response:**

```json
{
  "success": true,
  "data": {
    "batch_size": 4,
    "predictions": [
      {
        "customer_id": 123,
        "churn": {
          "customer_id": 123,
          "churn_probability": 0.1192,
          "risk_segment": "low_risk",
          "will_churn": 0,
          "confidence": 0.85
        },
        "ltv": {
          "customer_id": 123,
          "predicted_ltv": 39588.89,
          "ltv_segment": "high_value",
          "confidence": 0.8
        },
        "recommendations": [
          "VIP treatment - priority service",
          "Exclusive menu items access"
        ]
      }
    ]
  }
}
```

---

### 12. Get At-Risk Customers

**GET** `/customer/at-risk`

Identify customers at risk of churn.

**Query Parameters:**

- `restaurant_id` (string, UUID): Restaurant identifier
- `threshold` (float, default: 0.6): Churn probability threshold

**Response:**

```json
{
  "success": true,
  "data": {
    "analysis_type": "at_risk_customers",
    "threshold": 0.6,
    "at_risk_count": 0,
    "customers": []
  }
}
```

---

### 13. Get High-Value Customers

**GET** `/customer/high-value`

Identify high-value customers.

**Query Parameters:**

- `restaurant_id` (string, UUID): Restaurant identifier
- `ltv_percentile` (float, default: 75): LTV percentile threshold

**Response:**

```json
{
  "success": true,
  "data": {
    "analysis_type": "high_value_customers",
    "percentile_threshold": 75,
    "ltv_threshold": 39588.89,
    "high_value_count": 4,
    "customers": [
      {
        "customer_id": 123,
        "predicted_ltv": 39588.89,
        "ltv_segment": "high_value",
        "total_spent": 5000.0,
        "total_orders": 25
      }
    ]
  }
}
```

---

## INVENTORY OPTIMIZATION ENDPOINTS

### 14. Get Item Recommendation

**GET** `/inventory/recommendations`

Get inventory recommendation for a specific item.

**Query Parameters:**

- `restaurant_id` (string, UUID): Restaurant identifier
- `item_id` (integer): Item ID

**Response:**

```json
{
  "success": true,
  "data": {
    "item_id": 1,
    "current_stock": 50,
    "action": "maintain",
    "urgency": "low",
    "reason": "Stock level is healthy",
    "recommended_order_qty": 0,
    "generated_at": "2026-02-24T16:30:00"
  }
}
```

---

### 15. Get Batch Recommendations

**POST** `/inventory/batch-recommendations`

Get recommendations for all inventory items.

**Query Parameters:**

- `restaurant_id` (string, UUID): Restaurant identifier

**Response:**

```json
{
  "success": true,
  "data": {
    "batch_size": 10,
    "recommendations": [
      {
        "item_id": 1,
        "current_stock": 50,
        "action": "maintain",
        "urgency": "low",
        "reason": "Stock level is healthy",
        "recommended_order_qty": 0
      }
    ],
    "critical_count": 0,
    "high_count": 0
  }
}
```

---

### 16. Get Reorder Summary

**GET** `/inventory/reorder-summary`

Get summary of items needing reorder.

**Query Parameters:**

- `restaurant_id` (string, UUID): Restaurant identifier

**Response:**

```json
{
  "success": true,
  "data": {
    "summary_type": "reorder_summary",
    "items_needing_reorder": 0,
    "total_reorder_quantity": 0,
    "items": []
  }
}
```

---

### 17. Get Inventory Status

**GET** `/inventory/status`

Get overall inventory status report.

**Query Parameters:**

- `restaurant_id` (string, UUID): Restaurant identifier

**Response:**

```json
{
  "success": true,
  "data": {
    "report_type": "stock_status",
    "total_items": 10,
    "status_summary": {
      "healthy": 8,
      "medium": 2,
      "low": 0,
      "critical": 0
    },
    "status_details": {
      "healthy": [
        {
          "item_id": 1,
          "item_name": "Flour",
          "current_stock": 50,
          "projected_stock": 45,
          "days_until_stockout": 45
        }
      ]
    }
  }
}
```

---

### 18. Optimize Inventory

**POST** `/inventory/optimize`

Get comprehensive inventory optimization for an item.

**Query Parameters:**

- `restaurant_id` (string, UUID): Restaurant identifier
- `item_id` (integer): Item ID

**Response:**

```json
{
  "success": true,
  "data": {
    "item_id": 1,
    "optimization": {
      "reorder_point": 25.0,
      "safety_stock": 15.0,
      "optimal_order_quantity": 50.0,
      "orders_per_year": 7.3,
      "annual_holding_cost": 365.0
    },
    "current_status": {
      "current_stock": 50,
      "daily_consumption": 2.0,
      "annual_demand": 730
    },
    "forecast": {
      "projected_stock": 10,
      "days_until_stockout": 5,
      "will_stockout": false,
      "stock_status": "low"
    },
    "recommendation": {
      "item_id": 1,
      "current_stock": 50,
      "action": "maintain",
      "urgency": "low",
      "reason": "Stock level is healthy",
      "recommended_order_qty": 0
    }
  }
}
```

---

### 19. Get Waste Reduction Insights

**GET** `/inventory/waste-insights`

Get insights for waste reduction.

**Query Parameters:**

- `restaurant_id` (string, UUID): Restaurant identifier

**Response:**

```json
{
  "success": true,
  "data": {
    "analysis_type": "waste_reduction",
    "insights_count": 0,
    "insights": []
  }
}
```

---

### 20. Get Cost Analysis

**GET** `/inventory/cost-analysis`

Get inventory cost analysis.

**Query Parameters:**

- `restaurant_id` (string, UUID): Restaurant identifier

**Response:**

```json
{
  "success": true,
  "data": {
    "analysis_type": "cost_analysis",
    "total_items": 10,
    "total_holding_cost": 1825.0,
    "total_ordering_cost": 365.0,
    "total_inventory_cost": 2190.0,
    "items": [
      {
        "item_id": 1,
        "item_name": "Flour",
        "annual_demand": 730,
        "holding_cost": 182.5,
        "ordering_cost": 36.5,
        "total_cost": 219.0
      }
    ]
  }
}
```

---

## Error Handling

All endpoints return error responses in this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**

- `200`: Success
- `400`: Bad request (invalid parameters)
- `404`: Resource not found (model or data not found)
- `500`: Server error

---

## Example Usage

### Using cURL

```bash
# Predict demand
curl -X POST http://localhost:8000/api/predictions/demand \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_id": "a33877ad-36ac-420a-96d0-6f518e5af21b",
    "forecast_type": "hourly",
    "hours_ahead": 24
  }'

# Get kitchen bottlenecks
curl -X GET "http://localhost:8000/api/predictions/kitchen/bottlenecks?restaurant_id=a33877ad-36ac-420a-96d0-6f518e5af21b"

# Get at-risk customers
curl -X GET "http://localhost:8000/api/predictions/customer/at-risk?restaurant_id=a33877ad-36ac-420a-96d0-6f518e5af21b&threshold=0.6"
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000/api/predictions"
RESTAURANT_ID = "a33877ad-36ac-420a-96d0-6f518e5af21b"

# Predict demand
response = requests.post(
    f"{BASE_URL}/demand",
    json={
        "restaurant_id": RESTAURANT_ID,
        "forecast_type": "hourly",
        "hours_ahead": 24
    }
)
print(response.json())

# Get kitchen bottlenecks
response = requests.get(
    f"{BASE_URL}/kitchen/bottlenecks",
    params={"restaurant_id": RESTAURANT_ID}
)
print(response.json())
```

---

## Summary

**Total Endpoints: 20**

- **Demand Forecasting**: 4 endpoints
- **Kitchen Service**: 4 endpoints
- **Customer Analytics**: 5 endpoints
- **Inventory Optimization**: 7 endpoints

All endpoints are production-ready and fully integrated with the ML models.

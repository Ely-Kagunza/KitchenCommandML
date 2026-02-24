# API Reference

## Base URL

```
Production: https://ml-api.yourdomain.com
Staging: https://ml-api-staging.yourdomain.com
Development: http://localhost:8000
```

## Authentication

All API requests require authentication using an API key.

### Header Format

```http
Authorization: Bearer YOUR_API_KEY
```

### Example

```bash
curl -H "Authorization: Bearer sk_live_abc123..." \
     https://ml-api.yourdomain.com/api/predictions/demand
```

## Common Response Format

### Success Response

```json
{
  "success": true,
  "data": {
    // Response data
  },
  "metadata": {
    "model_version": "20260219_100000",
    "prediction_time_ms": 45,
    "cached": false
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "restaurant_id is required",
    "details": {}
  }
}
```

## Endpoints

### Health Check

Check API health and status.

**Endpoint**: `GET /api/health`

**Authentication**: Not required

**Response**:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-02-19T10:30:00Z",
  "services": {
    "database": "connected",
    "redis": "connected",
    "models": "loaded"
  }
}
```

---

### Demand Forecasting

#### Get Demand Forecast

Predict order volume for specified time period.

**Endpoint**: `GET /api/predictions/demand`

**Parameters**:

| Parameter     | Type    | Required | Description                                     |
| ------------- | ------- | -------- | ----------------------------------------------- |
| restaurant_id | integer | Yes      | Restaurant ID                                   |
| hours         | integer | No       | Forecast hours ahead (default: 24, max: 168)    |
| granularity   | string  | No       | 'hourly' or 'daily' (default: 'hourly')         |
| include_items | boolean | No       | Include item-level predictions (default: false) |

**Example Request**:

```bash
GET /api/predictions/demand?restaurant_id=1&hours=48&granularity=hourly
```

**Response**:

```json
{
  "success": true,
  "data": {
    "restaurant_id": 1,
    "forecast_start": "2026-02-19T11:00:00Z",
    "forecast_end": "2026-02-21T11:00:00Z",
    "granularity": "hourly",
    "predictions": [
      {
        "timestamp": "2026-02-19T11:00:00Z",
        "predicted_orders": 12,
        "confidence_interval": {
          "lower": 8,
          "upper": 16
        },
        "day_of_week": "Thursday",
        "hour": 11,
        "is_peak_hour": false
      },
      {
        "timestamp": "2026-02-19T12:00:00Z",
        "predicted_orders": 25,
        "confidence_interval": {
          "lower": 20,
          "upper": 30
        },
        "day_of_week": "Thursday",
        "hour": 12,
        "is_peak_hour": true
      }
    ],
    "summary": {
      "total_predicted_orders": 450,
      "avg_orders_per_hour": 9.4,
      "peak_hours": [12, 13, 18, 19, 20],
      "busiest_day": "Friday"
    }
  },
  "metadata": {
    "model_version": "20260219_100000",
    "prediction_time_ms": 120,
    "cached": false
  }
}
```

#### Get Item Demand Forecast

Predict demand for specific menu items.

**Endpoint**: `GET /api/predictions/demand/items`

**Parameters**:

| Parameter     | Type    | Required | Description                               |
| ------------- | ------- | -------- | ----------------------------------------- |
| restaurant_id | integer | Yes      | Restaurant ID                             |
| item_ids      | array   | No       | Specific item IDs (default: top 50 items) |
| hours         | integer | No       | Forecast hours ahead (default: 24)        |

**Example Request**:

```bash
GET /api/predictions/demand/items?restaurant_id=1&item_ids=10,20,30&hours=24
```

**Response**:

```json
{
  "success": true,
  "data": {
    "restaurant_id": 1,
    "items": [
      {
        "item_id": 10,
        "item_name": "Margherita Pizza",
        "category": "Pizza",
        "predicted_quantity": 45,
        "confidence_interval": {
          "lower": 38,
          "upper": 52
        },
        "hourly_breakdown": [
          {
            "hour": 11,
            "quantity": 3
          },
          {
            "hour": 12,
            "quantity": 8
          }
        ]
      }
    ]
  }
}
```

---

### Kitchen Performance

#### Predict Prep Time

Estimate preparation time for an order item.

**Endpoint**: `POST /api/predictions/kitchen/prep-time`

**Request Body**:

```json
{
  "restaurant_id": 1,
  "station_id": 5,
  "menu_item_id": 10,
  "quantity": 2,
  "has_modifiers": true,
  "current_queue_size": 3
}
```

**Response**:

```json
{
  "success": true,
  "data": {
    "predicted_prep_time_minutes": 8.5,
    "confidence_interval": {
      "lower": 6.5,
      "upper": 10.5
    },
    "queue_time_minutes": 5.0,
    "total_estimated_time_minutes": 13.5,
    "estimated_ready_at": "2026-02-19T11:13:30Z",
    "factors": {
      "item_complexity": "medium",
      "station_load": "moderate",
      "time_of_day": "peak"
    }
  },
  "metadata": {
    "model_version": "20260218_150000",
    "prediction_time_ms": 35
  }
}
```

#### Get Station Performance

Get performance metrics and predictions for a kitchen station.

**Endpoint**: `GET /api/predictions/kitchen/station/{station_id}`

**Parameters**:

| Parameter        | Type    | Required | Description                               |
| ---------------- | ------- | -------- | ----------------------------------------- |
| station_id       | integer | Yes      | Kitchen station ID                        |
| include_forecast | boolean | No       | Include workload forecast (default: true) |

**Response**:

```json
{
  "success": true,
  "data": {
    "station_id": 5,
    "station_name": "Grill Station",
    "current_metrics": {
      "queue_size": 3,
      "avg_prep_time_today": 7.2,
      "orders_completed_today": 45,
      "efficiency_score": 0.92
    },
    "forecast": {
      "next_hour_orders": 12,
      "peak_time": "12:00-13:00",
      "bottleneck_risk": "low"
    },
    "recommendations": [
      "Consider adding staff during 12:00-13:00",
      "Current performance is above average"
    ]
  }
}
```

---

### Customer Analytics

#### Predict Customer Churn

Get churn probability for a customer.

**Endpoint**: `GET /api/predictions/customer/churn/{customer_id}`

**Parameters**:

| Parameter   | Type    | Required | Description |
| ----------- | ------- | -------- | ----------- |
| customer_id | integer | Yes      | Customer ID |

**Response**:

```json
{
  "success": true,
  "data": {
    "customer_id": 123,
    "churn_probability": 0.35,
    "risk_level": "medium",
    "risk_factors": [
      {
        "factor": "days_since_last_order",
        "value": 45,
        "impact": "high"
      },
      {
        "factor": "order_frequency_decline",
        "value": -0.3,
        "impact": "medium"
      }
    ],
    "recommendations": [
      "Send personalized offer within 7 days",
      "Offer loyalty points bonus",
      "Remind of unused rewards"
    ],
    "predicted_churn_date": "2026-03-15"
  },
  "metadata": {
    "model_version": "20260215_100000",
    "prediction_time_ms": 25
  }
}
```

#### Predict Customer Lifetime Value

Get predicted lifetime value for a customer.

**Endpoint**: `GET /api/predictions/customer/ltv/{customer_id}`

**Parameters**:

| Parameter     | Type    | Required | Description                     |
| ------------- | ------- | -------- | ------------------------------- |
| customer_id   | integer | Yes      | Customer ID                     |
| period_months | integer | No       | Prediction period (default: 12) |

**Response**:

```json
{
  "success": true,
  "data": {
    "customer_id": 123,
    "predicted_ltv": 1250.5,
    "period_months": 12,
    "confidence_interval": {
      "lower": 980.0,
      "upper": 1520.0
    },
    "value_segment": "high_value",
    "breakdown": {
      "predicted_orders": 25,
      "avg_order_value": 50.02,
      "predicted_frequency": "bi-weekly"
    },
    "current_metrics": {
      "total_spent_to_date": 850.0,
      "orders_to_date": 17,
      "customer_since": "2025-06-15"
    }
  }
}
```

#### Batch Customer Predictions

Get predictions for multiple customers.

**Endpoint**: `POST /api/predictions/customer/batch`

**Request Body**:

```json
{
  "restaurant_id": 1,
  "customer_ids": [123, 456, 789],
  "predictions": ["churn", "ltv"]
}
```

**Response**:

```json
{
  "success": true,
  "data": {
    "customers": [
      {
        "customer_id": 123,
        "churn_probability": 0.35,
        "predicted_ltv": 1250.5,
        "risk_level": "medium",
        "value_segment": "high_value"
      },
      {
        "customer_id": 456,
        "churn_probability": 0.15,
        "predicted_ltv": 2100.0,
        "risk_level": "low",
        "value_segment": "high_value"
      }
    ]
  }
}
```

---

### Inventory Optimization

#### Get Reorder Recommendations

Get inventory reorder recommendations.

**Endpoint**: `GET /api/predictions/inventory/reorder`

**Parameters**:

| Parameter     | Type    | Required | Description                              |
| ------------- | ------- | -------- | ---------------------------------------- |
| restaurant_id | integer | Yes      | Restaurant ID                            |
| item_ids      | array   | No       | Specific item IDs (default: all items)   |
| urgency       | string  | No       | 'urgent', 'soon', 'all' (default: 'all') |

**Response**:

```json
{
  "success": true,
  "data": {
    "restaurant_id": 1,
    "recommendations": [
      {
        "item_id": 50,
        "item_name": "Tomato Sauce",
        "current_stock": 15.5,
        "unit": "liters",
        "reorder_point": 20.0,
        "recommended_order_quantity": 50.0,
        "urgency": "urgent",
        "estimated_stockout_date": "2026-02-22",
        "days_until_stockout": 3,
        "supplier": "Fresh Foods Co.",
        "estimated_cost": 125.0,
        "reasoning": "Current stock below reorder point. High consumption rate detected."
      },
      {
        "item_id": 51,
        "item_name": "Mozzarella Cheese",
        "current_stock": 25.0,
        "unit": "kg",
        "reorder_point": 30.0,
        "recommended_order_quantity": 40.0,
        "urgency": "soon",
        "estimated_stockout_date": "2026-02-28",
        "days_until_stockout": 9,
        "supplier": "Dairy Suppliers Ltd.",
        "estimated_cost": 800.0,
        "reasoning": "Approaching reorder point. Weekend demand expected."
      }
    ],
    "summary": {
      "total_items": 2,
      "urgent_items": 1,
      "total_estimated_cost": 925.0
    }
  }
}
```

#### Predict Stock Levels

Predict future stock levels based on demand forecast.

**Endpoint**: `GET /api/predictions/inventory/stock-forecast`

**Parameters**:

| Parameter     | Type    | Required | Description                         |
| ------------- | ------- | -------- | ----------------------------------- |
| restaurant_id | integer | Yes      | Restaurant ID                       |
| item_id       | integer | Yes      | Inventory item ID                   |
| days          | integer | No       | Forecast days (default: 7, max: 30) |

**Response**:

```json
{
  "success": true,
  "data": {
    "item_id": 50,
    "item_name": "Tomato Sauce",
    "current_stock": 15.5,
    "unit": "liters",
    "forecast": [
      {
        "date": "2026-02-19",
        "predicted_stock": 12.3,
        "predicted_consumption": 3.2,
        "stockout_risk": "low"
      },
      {
        "date": "2026-02-20",
        "predicted_stock": 8.5,
        "predicted_consumption": 3.8,
        "stockout_risk": "medium"
      },
      {
        "date": "2026-02-21",
        "predicted_stock": 4.2,
        "predicted_consumption": 4.3,
        "stockout_risk": "high"
      },
      {
        "date": "2026-02-22",
        "predicted_stock": 0.0,
        "predicted_consumption": 4.2,
        "stockout_risk": "critical"
      }
    ],
    "alerts": [
      {
        "type": "stockout_warning",
        "date": "2026-02-22",
        "message": "Predicted stockout in 3 days"
      }
    ]
  }
}
```

---

### Model Management

#### Get Model Info

Get information about deployed models.

**Endpoint**: `GET /api/models/info`

**Parameters**:

| Parameter     | Type    | Required | Description         |
| ------------- | ------- | -------- | ------------------- |
| restaurant_id | integer | Yes      | Restaurant ID       |
| model_type    | string  | No       | Specific model type |

**Response**:

```json
{
  "success": true,
  "data": {
    "models": [
      {
        "model_type": "demand_forecasting",
        "version": "20260219_100000",
        "trained_at": "2026-02-19T10:00:00Z",
        "status": "active",
        "metrics": {
          "mae": 4.2,
          "rmse": 6.8,
          "r2": 0.89
        },
        "training_data": {
          "records": 15000,
          "date_range": "2025-08-19 to 2026-02-19"
        }
      },
      {
        "model_type": "kitchen_performance",
        "version": "20260218_150000",
        "trained_at": "2026-02-18T15:00:00Z",
        "status": "active",
        "metrics": {
          "mae": 1.8,
          "rmse": 2.5,
          "r2": 0.82
        }
      }
    ]
  }
}
```

#### Trigger Model Retraining

Manually trigger model retraining.

**Endpoint**: `POST /api/models/retrain`

**Request Body**:

```json
{
  "restaurant_id": 1,
  "model_type": "demand_forecasting",
  "priority": "high"
}
```

**Response**:

```json
{
  "success": true,
  "data": {
    "job_id": "retrain_demand_1_20260219_110000",
    "status": "queued",
    "estimated_completion": "2026-02-19T11:30:00Z",
    "message": "Model retraining job queued successfully"
  }
}
```

---

## Rate Limiting

API requests are rate-limited to ensure fair usage.

**Limits**:

- Free tier: 100 requests/hour
- Standard tier: 1000 requests/hour
- Premium tier: 10000 requests/hour

**Headers**:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1645275600
```

**Rate Limit Exceeded Response**:

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 30 minutes.",
    "retry_after": 1800
  }
}
```

## Error Codes

| Code                | HTTP Status | Description                          |
| ------------------- | ----------- | ------------------------------------ |
| INVALID_PARAMETER   | 400         | Missing or invalid request parameter |
| UNAUTHORIZED        | 401         | Invalid or missing API key           |
| FORBIDDEN           | 403         | Insufficient permissions             |
| NOT_FOUND           | 404         | Resource not found                   |
| RATE_LIMIT_EXCEEDED | 429         | Too many requests                    |
| MODEL_NOT_READY     | 503         | Model not trained or unavailable     |
| INTERNAL_ERROR      | 500         | Internal server error                |

## Webhooks (Optional)

Configure webhooks to receive predictions proactively.

**Webhook Payload**:

```json
{
  "event": "prediction.completed",
  "timestamp": "2026-02-19T11:00:00Z",
  "data": {
    "model_type": "demand_forecasting",
    "restaurant_id": 1,
    "predictions": {
      // Prediction data
    }
  }
}
```

**Webhook Events**:

- `prediction.completed`: Prediction generated
- `model.trained`: Model training completed
- `alert.triggered`: Alert condition met (e.g., stockout warning)

---

## SDK Examples

### Python

```python
import requests

class MLServiceClient:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def get_demand_forecast(self, restaurant_id: int, hours: int = 24):
        """Get demand forecast."""
        response = requests.get(
            f'{self.base_url}/api/predictions/demand',
            params={'restaurant_id': restaurant_id, 'hours': hours},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def predict_prep_time(self, data: dict):
        """Predict kitchen prep time."""
        response = requests.post(
            f'{self.base_url}/api/predictions/kitchen/prep-time',
            json=data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

# Usage
client = MLServiceClient(
    api_key='sk_live_abc123...',
    base_url='https://ml-api.yourdomain.com'
)

forecast = client.get_demand_forecast(restaurant_id=1, hours=48)
print(forecast['data']['summary'])
```

### JavaScript/TypeScript

```typescript
class MLServiceClient {
  private apiKey: string
  private baseUrl: string

  constructor(apiKey: string, baseUrl: string) {
    this.apiKey = apiKey
    this.baseUrl = baseUrl
  }

  async getDemandForecast(restaurantId: number, hours: number = 24) {
    const response = await fetch(
      `${this.baseUrl}/api/predictions/demand?restaurant_id=${restaurantId}&hours=${hours}`,
      {
        headers: {
          Authorization: `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
      },
    )

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`)
    }

    return await response.json()
  }

  async predictPrepTime(data: any) {
    const response = await fetch(
      `${this.baseUrl}/api/predictions/kitchen/prep-time`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      },
    )

    return await response.json()
  }
}

// Usage
const client = new MLServiceClient(
  'sk_live_abc123...',
  'https://ml-api.yourdomain.com',
)

const forecast = await client.getDemandForecast(1, 48)
console.log(forecast.data.summary)
```

---

**Next**: [Deployment Guide](./05-DEPLOYMENT.md)

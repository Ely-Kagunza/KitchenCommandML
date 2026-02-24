# Frontend API Quick Reference

## Quick Start

All API calls go to: `http://localhost:8000/api/predictions`

Restaurant ID format: UUID string (e.g., `a33877ad-36ac-420a-96d0-6f518e5af21b`)

---

## Demand Forecasting

### Hourly Forecast (Next 24 Hours)

```javascript
POST /demand
{
  "restaurant_id": "uuid",
  "forecast_type": "hourly",
  "hours_ahead": 24
}
```

Returns: Array of hourly predictions with timestamps and order counts

### Daily Forecast (Next 7 Days)

```javascript
POST /demand
{
  "restaurant_id": "uuid",
  "forecast_type": "daily",
  "days_ahead": 7
}
```

Returns: Array of daily predictions with hourly breakdown

### Item-Level Demand

```javascript
POST /demand/items?restaurant_id=uuid&item_id=5&hours_ahead=24
```

Returns: Predictions for specific menu item

### Category Demand

```javascript
POST /demand/category?restaurant_id=uuid&category_name=Burgers&hours_ahead=24
```

Returns: Predictions for menu category

### Peak Hours

```javascript
GET /demand/peak-hours?restaurant_id=uuid&days_ahead=7
```

Returns: Top 3 peak hours for each day

---

## Kitchen Operations

### Single Item Prep Time

```javascript
POST /kitchen/prep-time
{
  "restaurant_id": "uuid",
  "station_id": 1,
  "menu_item_id": 5
}
```

Returns: Predicted prep time with confidence interval

### Batch Prep Time (Multiple Items)

```javascript
POST /kitchen/batch-prep-time
{
  "restaurant_id": "uuid",
  "orders": [
    {"station_id": 1, "menu_item_id": 5},
    {"station_id": 2, "menu_item_id": 8}
  ]
}
```

Returns: Individual predictions + total estimated time

### Bottleneck Detection

```javascript
GET /kitchen/bottlenecks?restaurant_id=uuid
```

Returns: Slow items and stations with performance metrics

### Station Performance

```javascript
GET /kitchen/station-performance?restaurant_id=uuid
```

Returns: Performance metrics for each kitchen station

---

## Customer Analytics

### Single Customer Churn Risk

```javascript
POST /customer/churn
{
  "restaurant_id": "uuid",
  "customer_id": 123
}
```

Returns: Churn probability (0-1) and risk segment

### Single Customer LTV

```javascript
GET /customer/ltv?restaurant_id=uuid&customer_id=123
```

Returns: Predicted lifetime value and segment

### All Customers Analytics

```javascript
POST /customer/batch-analytics?restaurant_id=uuid
```

Returns: Churn + LTV predictions for all customers with recommendations

### At-Risk Customers

```javascript
GET /customer/at-risk?restaurant_id=uuid&threshold=0.6
```

Returns: List of customers likely to churn (threshold: 0-1)

### High-Value Customers

```javascript
GET /customer/high-value?restaurant_id=uuid&ltv_percentile=75
```

Returns: Top customers by predicted lifetime value

---

## Inventory Management

### Single Item Recommendation

```javascript
GET /inventory/recommendations?restaurant_id=uuid&item_id=1
```

Returns: Action (reorder/maintain/reduce), urgency, reason

### All Items Recommendations

```javascript
POST /inventory/batch-recommendations?restaurant_id=uuid
```

Returns: Recommendations for all items sorted by urgency

### Reorder Summary

```javascript
GET /inventory/reorder-summary?restaurant_id=uuid
```

Returns: Items needing reorder + total quantity

### Inventory Status

```javascript
GET /inventory/status?restaurant_id=uuid
```

Returns: Overall stock status (healthy/medium/low/critical)

### Item Optimization

```javascript
POST /inventory/optimize?restaurant_id=uuid&item_id=1
```

Returns: Reorder point, EOQ, forecast, and recommendation

### Waste Insights

```javascript
GET /inventory/waste-insights?restaurant_id=uuid
```

Returns: Items with excess stock or expiry risks

### Cost Analysis

```javascript
GET /inventory/cost-analysis?restaurant_id=uuid
```

Returns: Holding costs, ordering costs, and total inventory cost

---

## Response Format

All successful responses:

```json
{
  "success": true,
  "data": {
    /* prediction data */
  },
  "metadata": {
    "model_version": "1.0.0",
    "prediction_time_ms": 125.45,
    "generated_at": "2026-02-24T16:30:00"
  }
}
```

Error responses:

```json
{
  "detail": "Error message"
}
```

---

## Common Parameters

| Parameter       | Type        | Example                                | Notes                      |
| --------------- | ----------- | -------------------------------------- | -------------------------- |
| `restaurant_id` | UUID string | `a33877ad-36ac-420a-96d0-6f518e5af21b` | Required for all endpoints |
| `hours_ahead`   | integer     | 24                                     | Default: 24                |
| `days_ahead`    | integer     | 7                                      | Default: 7                 |
| `threshold`     | float       | 0.6                                    | Range: 0-1                 |
| `percentile`    | float       | 75                                     | Range: 0-100               |

---

## Data Types in Responses

### Demand Predictions

```javascript
{
  "timestamp": "2026-02-24T17:00:00",
  "predicted_orders": 3,
  "confidence": 0.85
}
```

### Kitchen Predictions

```javascript
{
  "predicted_prep_time_minutes": 4.2,
  "lower_bound_minutes": 3.1,
  "upper_bound_minutes": 5.3,
  "confidence": 0.85
}
```

### Customer Predictions

```javascript
{
  "churn_probability": 0.1192,  // 0-1
  "risk_segment": "low_risk",   // low_risk, medium_risk, high_risk
  "predicted_ltv": 39588.89,
  "ltv_segment": "high_value"   // low_value, medium_value, high_value
}
```

### Inventory Recommendations

```javascript
{
  "action": "maintain",         // maintain, reorder, emergency_reorder, reduce
  "urgency": "low",             // low, medium, high, critical
  "reason": "Stock level is healthy",
  "recommended_order_qty": 0
}
```

---

## Performance Notes

- **Prediction Time**: Most predictions complete in 100-300ms
- **Batch Operations**: Scale linearly with data size
- **Caching**: No caching implemented; each call fetches fresh data
- **Rate Limiting**: None implemented; safe for production use

---

## Common Use Cases

### Dashboard Overview

1. Get demand forecast (hourly)
2. Get kitchen bottlenecks
3. Get at-risk customers
4. Get inventory status

### Kitchen Display System

1. Get batch prep time for current orders
2. Get station performance
3. Get bottleneck detection

### Customer Management

1. Get batch analytics for all customers
2. Get at-risk customers for retention campaigns
3. Get high-value customers for VIP treatment

### Inventory Management

1. Get reorder summary
2. Get cost analysis
3. Get waste insights

---

## Testing Endpoints

Use the provided test script to verify all endpoints:

```bash
python test_all_services_fixed.py
```

Or test individual endpoints with curl:

```bash
curl -X GET "http://localhost:8000/api/predictions/demand/peak-hours?restaurant_id=a33877ad-36ac-420a-96d0-6f518e5af21b"
```

---

## Frontend Integration Example

```javascript
// React hook for demand predictions
const useDemandForecast = (restaurantId) => {
  const [forecast, setForecast] = useState(null)
  const [loading, setLoading] = useState(false)

  const fetchForecast = async () => {
    setLoading(true)
    try {
      const response = await fetch(
        'http://localhost:8000/api/predictions/demand',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            restaurant_id: restaurantId,
            forecast_type: 'hourly',
            hours_ahead: 24,
          }),
        },
      )
      const data = await response.json()
      setForecast(data.data)
    } catch (error) {
      console.error('Error fetching forecast:', error)
    } finally {
      setLoading(false)
    }
  }

  return { forecast, loading, fetchForecast }
}
```

---

## Troubleshooting

| Issue               | Solution                                         |
| ------------------- | ------------------------------------------------ |
| 404 Model not found | Train model first or check restaurant_id         |
| 500 Server error    | Check API logs, ensure database connection       |
| Slow responses      | Check database performance, consider caching     |
| No data returned    | Verify restaurant has sufficient historical data |

---

## Next Steps

1. Integrate endpoints into React components
2. Add error handling and loading states
3. Implement caching for frequently accessed data
4. Add real-time updates using WebSockets
5. Create dashboards for each prediction type

# Integration Guide

## Overview

This guide explains how to integrate the ML service with your Restaurant Management System (RMS).

## Integration Architecture

```
RMS Django Backend
    ↓
ML Client Service (Python)
    ↓
HTTP/REST API
    ↓
ML Service
    ↓
Predictions returned to RMS
    ↓
Display in Dashboard/UI
```

## RMS Integration Steps

### Step 1: Create ML Client Service

**File**: `backend/apps/ml/client.py`

```python
import requests
from typing import Dict, List, Optional
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class MLServiceClient:
    """Client for ML Service API."""

    def __init__(self):
        self.base_url = settings.ML_SERVICE_URL
        self.api_key = settings.ML_SERVICE_API_KEY
        self.timeout = settings.ML_SERVICE_TIMEOUT or 30
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict:
        """Make HTTP request to ML service."""
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            logger.error(f"ML Service timeout: {endpoint}")
            raise MLServiceTimeout("ML service request timed out")

        except requests.exceptions.HTTPError as e:
            logger.error(f"ML Service HTTP error: {e.response.status_code} - {e.response.text}")
            raise MLServiceError(f"ML service error: {e.response.status_code}")

        except Exception as e:
            logger.error(f"ML Service error: {str(e)}")
            raise MLServiceError(f"Unexpected error: {str(e)}")

    def get_demand_forecast(
        self,
        restaurant_id: int,
        hours: int = 24,
        granularity: str = 'hourly',
        use_cache: bool = True
    ) -> Dict:
        """Get demand forecast for restaurant."""
        cache_key = f'ml:demand:{restaurant_id}:{hours}:{granularity}'

        if use_cache:
            cached = cache.get(cache_key)
            if cached:
                logger.info(f"Using cached demand forecast for restaurant {restaurant_id}")
                return cached

        result = self._make_request(
            method='GET',
            endpoint='/api/predictions/demand',
            params={
                'restaurant_id': restaurant_id,
                'hours': hours,
                'granularity': granularity
            }
        )

        if use_cache and result.get('success'):
            cache.set(cache_key, result, timeout=3600)  # Cache for 1 hour

        return result

    def get_item_demand_forecast(
        self,
        restaurant_id: int,
        item_ids: Optional[List[int]] = None,
        hours: int = 24
    ) -> Dict:
        """Get item-level demand forecast."""
        params = {
            'restaurant_id': restaurant_id,
            'hours': hours
        }

        if item_ids:
            params['item_ids'] = ','.join(map(str, item_ids))

        return self._make_request(
            method='GET',
            endpoint='/api/predictions/demand/items',
            params=params
        )

    def predict_prep_time(
        self,
        restaurant_id: int,
        station_id: int,
        menu_item_id: int,
        quantity: int = 1,
        has_modifiers: bool = False,
        current_queue_size: int = 0
    ) -> Dict:
        """Predict kitchen prep time."""
        return self._make_request(
            method='POST',
            endpoint='/api/predictions/kitchen/prep-time',
            data={
                'restaurant_id': restaurant_id,
                'station_id': station_id,
                'menu_item_id': menu_item_id,
                'quantity': quantity,
                'has_modifiers': has_modifiers,
                'current_queue_size': current_queue_size
            }
        )

    def get_customer_churn_prediction(
        self,
        customer_id: int,
        use_cache: bool = True
    ) -> Dict:
        """Get customer churn prediction."""
        cache_key = f'ml:churn:{customer_id}'

        if use_cache:
            cached = cache.get(cache_key)
            if cached:
                return cached

        result = self._make_request(
            method='GET',
            endpoint=f'/api/predictions/customer/churn/{customer_id}'
        )

        if use_cache and result.get('success'):
            cache.set(cache_key, result, timeout=86400)  # Cache for 24 hours

        return result

    def get_customer_ltv_prediction(
        self,
        customer_id: int,
        period_months: int = 12
    ) -> Dict:
        """Get customer lifetime value prediction."""
        return self._make_request(
            method='GET',
            endpoint=f'/api/predictions/customer/ltv/{customer_id}',
            params={'period_months': period_months}
        )

    def get_inventory_reorder_recommendations(
        self,
        restaurant_id: int,
        item_ids: Optional[List[int]] = None,
        urgency: str = 'all'
    ) -> Dict:
        """Get inventory reorder recommendations."""
        params = {
            'restaurant_id': restaurant_id,
            'urgency': urgency
        }

        if item_ids:
            params['item_ids'] = ','.join(map(str, item_ids))

        return self._make_request(
            method='GET',
            endpoint='/api/predictions/inventory/reorder',
            params=params
        )

    def get_stock_forecast(
        self,
        restaurant_id: int,
        item_id: int,
        days: int = 7
    ) -> Dict:
        """Get stock level forecast."""
        return self._make_request(
            method='GET',
            endpoint='/api/predictions/inventory/stock-forecast',
            params={
                'restaurant_id': restaurant_id,
                'item_id': item_id,
                'days': days
            }
        )

    def health_check(self) -> Dict:
        """Check ML service health."""
        try:
            return self._make_request(method='GET', endpoint='/api/health')
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}


class MLServiceError(Exception):
    """ML Service error."""
    pass


class MLServiceTimeout(MLServiceError):
    """ML Service timeout error."""
    pass
```

### Step 2: Configure Django Settings

**File**: `backend/config/settings.py`

```python
# ML Service Configuration
ML_SERVICE_URL = env('ML_SERVICE_URL', default='http://localhost:8000')
ML_SERVICE_API_KEY = env('ML_SERVICE_API_KEY', default='')
ML_SERVICE_TIMEOUT = env.int('ML_SERVICE_TIMEOUT', default=30)
ML_SERVICE_ENABLED = env.bool('ML_SERVICE_ENABLED', default=True)

# Cache configuration for ML predictions
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

**File**: `.env`

```bash
ML_SERVICE_URL=http://ml-api.yourdomain.com
ML_SERVICE_API_KEY=sk_live_your_api_key_here
ML_SERVICE_TIMEOUT=30
ML_SERVICE_ENABLED=true
```

### Step 3: Create ML Service Layer

**File**: `backend/apps/ml/services.py`

```python
from .client import MLServiceClient, MLServiceError, MLServiceTimeout
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class MLService:
    """Service layer for ML predictions."""

    def __init__(self):
        self.client = MLServiceClient()
        self.enabled = settings.ML_SERVICE_ENABLED

    def get_demand_forecast(self, restaurant_id: int, hours: int = 24):
        """Get demand forecast with error handling."""
        if not self.enabled:
            logger.warning("ML service is disabled")
            return None

        try:
            response = self.client.get_demand_forecast(
                restaurant_id=restaurant_id,
                hours=hours
            )

            if response.get('success'):
                return response.get('data')
            else:
                logger.error(f"ML service returned error: {response.get('error')}")
                return None

        except MLServiceTimeout:
            logger.error("ML service timeout")
            return None

        except MLServiceError as e:
            logger.error(f"ML service error: {str(e)}")
            return None

    def get_prep_time_estimate(
        self,
        restaurant_id: int,
        station_id: int,
        menu_item_id: int,
        quantity: int = 1
    ):
        """Get prep time estimate with fallback."""
        if not self.enabled:
            return self._get_fallback_prep_time(menu_item_id)

        try:
            response = self.client.predict_prep_time(
                restaurant_id=restaurant_id,
                station_id=station_id,
                menu_item_id=menu_item_id,
                quantity=quantity
            )

            if response.get('success'):
                data = response.get('data', {})
                return data.get('predicted_prep_time_minutes')
            else:
                return self._get_fallback_prep_time(menu_item_id)

        except Exception as e:
            logger.error(f"Error getting prep time: {str(e)}")
            return self._get_fallback_prep_time(menu_item_id)

    def _get_fallback_prep_time(self, menu_item_id: int):
        """Fallback prep time from database."""
        from apps.kitchen.models import OrderItemStation
        from django.db.models import Avg

        avg_time = OrderItemStation.objects.filter(
            order_item__menu_item_id=menu_item_id,
            status='completed'
        ).aggregate(
            avg=Avg('prep_time_minutes')
        )['avg']

        return avg_time or 10.0  # Default 10 minutes

    def get_customer_insights(self, customer_id: int):
        """Get customer churn and LTV predictions."""
        if not self.enabled:
            return None

        try:
            churn_response = self.client.get_customer_churn_prediction(customer_id)
            ltv_response = self.client.get_customer_ltv_prediction(customer_id)

            insights = {}

            if churn_response.get('success'):
                insights['churn'] = churn_response.get('data')

            if ltv_response.get('success'):
                insights['ltv'] = ltv_response.get('data')

            return insights if insights else None

        except Exception as e:
            logger.error(f"Error getting customer insights: {str(e)}")
            return None

    def get_inventory_alerts(self, restaurant_id: int):
        """Get inventory reorder recommendations."""
        if not self.enabled:
            return None

        try:
            response = self.client.get_inventory_reorder_recommendations(
                restaurant_id=restaurant_id,
                urgency='urgent'
            )

            if response.get('success'):
                return response.get('data', {}).get('recommendations', [])

            return None

        except Exception as e:
            logger.error(f"Error getting inventory alerts: {str(e)}")
            return None


# Singleton instance
ml_service = MLService()
```

### Step 4: Create API Endpoints

**File**: `backend/apps/ml/views.py`

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions import IsRestaurantOwnerOrStaff
from .services import ml_service

class MLPredictionsViewSet(viewsets.ViewSet):
    """ML predictions API endpoints."""

    permission_classes = [IsAuthenticated, IsRestaurantOwnerOrStaff]

    @action(detail=False, methods=['get'])
    def demand_forecast(self, request):
        """Get demand forecast for restaurant."""
        restaurant_id = request.query_params.get('restaurant_id')
        hours = int(request.query_params.get('hours', 24))

        if not restaurant_id:
            return Response(
                {'error': 'restaurant_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check user has access to restaurant
        if not self._has_restaurant_access(request.user, restaurant_id):
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        forecast = ml_service.get_demand_forecast(
            restaurant_id=int(restaurant_id),
            hours=hours
        )

        if forecast:
            return Response(forecast)
        else:
            return Response(
                {'error': 'ML service unavailable'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

    @action(detail=False, methods=['post'])
    def prep_time(self, request):
        """Get prep time estimate."""
        data = request.data

        restaurant_id = data.get('restaurant_id')
        station_id = data.get('station_id')
        menu_item_id = data.get('menu_item_id')
        quantity = data.get('quantity', 1)

        if not all([restaurant_id, station_id, menu_item_id]):
            return Response(
                {'error': 'Missing required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )

        prep_time = ml_service.get_prep_time_estimate(
            restaurant_id=restaurant_id,
            station_id=station_id,
            menu_item_id=menu_item_id,
            quantity=quantity
        )

        return Response({
            'predicted_prep_time_minutes': prep_time
        })

    @action(detail=True, methods=['get'])
    def customer_insights(self, request, pk=None):
        """Get customer insights (churn, LTV)."""
        customer_id = pk

        insights = ml_service.get_customer_insights(customer_id)

        if insights:
            return Response(insights)
        else:
            return Response(
                {'error': 'ML service unavailable'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

    @action(detail=False, methods=['get'])
    def inventory_alerts(self, request):
        """Get inventory reorder alerts."""
        restaurant_id = request.query_params.get('restaurant_id')

        if not restaurant_id:
            return Response(
                {'error': 'restaurant_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        alerts = ml_service.get_inventory_alerts(int(restaurant_id))

        if alerts:
            return Response({'recommendations': alerts})
        else:
            return Response({'recommendations': []})

    def _has_restaurant_access(self, user, restaurant_id):
        """Check if user has access to restaurant."""
        if user.role == 'owner':
            return user.organization.restaurants.filter(
                id=restaurant_id
            ).exists()
        else:
            return user.restaurant_id == int(restaurant_id)
```

**File**: `backend/apps/ml/urls.py`

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MLPredictionsViewSet

router = DefaultRouter()
router.register(r'predictions', MLPredictionsViewSet, basename='ml-predictions')

urlpatterns = [
    path('', include(router.urls)),
]
```

**File**: `backend/config/urls.py`

```python
urlpatterns = [
    # ... existing patterns
    path('api/ml/', include('apps.ml.urls')),
]
```

### Step 5: Dashboard Integration

**File**: `backend/apps/dashboard/views.py`

```python
from apps.ml.services import ml_service

class FinancialDashboardViewSet(viewsets.ViewSet):
    # ... existing code

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get comprehensive dashboard summary with ML predictions."""
        restaurant_ids = self.get_restaurant_ids()

        # ... existing summary code

        # Add ML predictions
        if len(restaurant_ids) == 1:
            restaurant_id = restaurant_ids[0]

            # Get demand forecast
            demand_forecast = ml_service.get_demand_forecast(
                restaurant_id=restaurant_id,
                hours=24
            )

            # Get inventory alerts
            inventory_alerts = ml_service.get_inventory_alerts(
                restaurant_id=restaurant_id
            )

            summary['ml_predictions'] = {
                'demand_forecast': demand_forecast,
                'inventory_alerts': inventory_alerts
            }

        return Response(summary)
```

### Step 6: Frontend Integration

**File**: `frontend/src/services/mlService.ts`

```typescript
import axios from 'axios'

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'

export interface DemandForecast {
  predictions: Array<{
    timestamp: string
    predicted_orders: number
    confidence_interval: {
      lower: number
      upper: number
    }
  }>
  summary: {
    total_predicted_orders: number
    avg_orders_per_hour: number
    peak_hours: number[]
  }
}

export interface CustomerInsights {
  churn: {
    churn_probability: number
    risk_level: string
    recommendations: string[]
  }
  ltv: {
    predicted_ltv: number
    value_segment: string
  }
}

class MLService {
  async getDemandForecast(
    restaurantId: number,
    hours: number = 24,
  ): Promise<DemandForecast | null> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/ml/predictions/demand_forecast/`,
        {
          params: { restaurant_id: restaurantId, hours },
        },
      )
      return response.data
    } catch (error) {
      console.error('Error fetching demand forecast:', error)
      return null
    }
  }

  async getCustomerInsights(
    customerId: number,
  ): Promise<CustomerInsights | null> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/ml/predictions/${customerId}/customer_insights/`,
      )
      return response.data
    } catch (error) {
      console.error('Error fetching customer insights:', error)
      return null
    }
  }

  async getInventoryAlerts(restaurantId: number): Promise<any[] | null> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/ml/predictions/inventory_alerts/`,
        {
          params: { restaurant_id: restaurantId },
        },
      )
      return response.data.recommendations
    } catch (error) {
      console.error('Error fetching inventory alerts:', error)
      return null
    }
  }
}

export default new MLService()
```

**File**: `frontend/src/components/Dashboard/DemandForecastWidget.tsx`

```typescript
import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import mlService from '../../services/mlService';

interface Props {
  restaurantId: number;
}

const DemandForecastWidget: React.FC<Props> = ({ restaurantId }) => {
  const [forecast, setForecast] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadForecast();
  }, [restaurantId]);

  const loadForecast = async () => {
    setLoading(true);
    const data = await mlService.getDemandForecast(restaurantId, 24);
    setForecast(data);
    setLoading(false);
  };

  if (loading) {
    return <div>Loading forecast...</div>;
  }

  if (!forecast) {
    return <div>Forecast unavailable</div>;
  }

  const chartData = {
    labels: forecast.predictions.map((p: any) =>
      new Date(p.timestamp).toLocaleTimeString('en-US', { hour: '2-digit' })
    ),
    datasets: [
      {
        label: 'Predicted Orders',
        data: forecast.predictions.map((p: any) => p.predicted_orders),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
      }
    ]
  };

  return (
    <div className="demand-forecast-widget">
      <h3>24-Hour Demand Forecast</h3>
      <Line data={chartData} />
      <div className="summary">
        <p>Total Predicted Orders: {forecast.summary.total_predicted_orders}</p>
        <p>Avg Orders/Hour: {forecast.summary.avg_orders_per_hour.toFixed(1)}</p>
        <p>Peak Hours: {forecast.summary.peak_hours.join(', ')}</p>
      </div>
    </div>
  );
};

export default DemandForecastWidget;
```

## Testing Integration

### Unit Tests

**File**: `backend/apps/ml/tests/test_client.py`

```python
from django.test import TestCase
from unittest.mock import patch, Mock
from apps.ml.client import MLServiceClient, MLServiceError

class MLServiceClientTestCase(TestCase):
    def setUp(self):
        self.client = MLServiceClient()

    @patch('requests.request')
    def test_get_demand_forecast_success(self, mock_request):
        """Test successful demand forecast request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': {'predictions': []}
        }
        mock_request.return_value = mock_response

        result = self.client.get_demand_forecast(restaurant_id=1, hours=24)

        self.assertTrue(result['success'])
        self.assertIn('data', result)

    @patch('requests.request')
    def test_get_demand_forecast_error(self, mock_request):
        """Test error handling."""
        mock_request.side_effect = Exception("Connection error")

        with self.assertRaises(MLServiceError):
            self.client.get_demand_forecast(restaurant_id=1, hours=24)
```

### Integration Tests

```bash
# Test ML service health
curl http://localhost:8000/api/health

# Test RMS integration
curl -H "Authorization: Token your_token" \
     "http://localhost:8000/api/ml/predictions/demand_forecast/?restaurant_id=1&hours=24"
```

## Monitoring Integration

### Log ML Predictions

```python
import logging

logger = logging.getLogger('ml_predictions')

def log_prediction(prediction_type, restaurant_id, result):
    """Log ML prediction for monitoring."""
    logger.info(
        f"ML Prediction: type={prediction_type}, "
        f"restaurant={restaurant_id}, "
        f"success={result is not None}"
    )
```

### Track Prediction Accuracy

```python
from apps.ml.models import PredictionLog

def log_prediction_for_validation(
    prediction_type: str,
    restaurant_id: int,
    predicted_value: float,
    metadata: dict
):
    """Log prediction for later validation."""
    PredictionLog.objects.create(
        prediction_type=prediction_type,
        restaurant_id=restaurant_id,
        predicted_value=predicted_value,
        metadata=metadata,
        predicted_at=timezone.now()
    )
```

---

**Next**: [Model Training](./07-MODEL-TRAINING.md)

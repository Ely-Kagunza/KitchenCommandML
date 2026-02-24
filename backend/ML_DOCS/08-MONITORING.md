# Monitoring & Maintenance

## Overview

Comprehensive monitoring ensures ML models perform reliably and maintain accuracy over time.

## Monitoring Stack

```
Application Metrics → Prometheus → Grafana Dashboards
Logs → ELK Stack / CloudWatch
Model Performance → Custom Tracking → Alerts
```

## Key Metrics to Monitor

### 1. API Performance Metrics

**Metrics**:

- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (%)
- Cache hit rate (%)
- Concurrent requests

**Prometheus Configuration**:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'ml-api'
    scrape_interval: 15s
    static_configs:
      - targets: ['ml-api:8000']
    metrics_path: '/metrics'
```

**FastAPI Metrics Endpoint**:

```python
# src/api/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response
import time

# Metrics
request_count = Counter(
    'ml_api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'ml_api_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

prediction_count = Counter(
    'ml_predictions_total',
    'Total predictions made',
    ['model_type', 'restaurant_id']
)

cache_hits = Counter(
    'ml_cache_hits_total',
    'Cache hits',
    ['cache_type']
)

active_models = Gauge(
    'ml_active_models',
    'Number of loaded models',
    ['model_type']
)

@app.get('/metrics')
def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type='text/plain'
    )

# Middleware to track metrics
@app.middleware("http")
async def track_metrics(request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time

    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response
```

### 2. Model Performance Metrics

**Metrics**:

- Prediction accuracy (MAE, RMSE, R²)
- Model drift detection
- Feature importance changes
- Training time
- Model size

**Tracking Implementation**:

```python
# src/monitoring/model_monitor.py
from typing import Dict, List
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ModelPerformanceMonitor:
    """Monitor model performance in production."""

    def __init__(self, db_connection):
        self.db = db_connection

    def log_prediction(
        self,
        model_type: str,
        restaurant_id: int,
        prediction: float,
        features: Dict,
        actual: float = None
    ):
        """Log prediction for monitoring."""
        self.db.execute("""
            INSERT INTO ml_prediction_logs
            (model_type, restaurant_id, prediction, features, actual, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            model_type,
            restaurant_id,
            prediction,
            json.dumps(features),
            actual,
            datetime.now()
        ))

    def calculate_recent_accuracy(
        self,
        model_type: str,
        restaurant_id: int,
        days: int = 7
    ) -> Dict:
        """Calculate accuracy over recent period."""
        cutoff = datetime.now() - timedelta(days=days)

        results = self.db.query("""
            SELECT prediction, actual
            FROM ml_prediction_logs
            WHERE model_type = %s
              AND restaurant_id = %s
              AND actual IS NOT NULL
              AND created_at >= %s
        """, (model_type, restaurant_id, cutoff))

        if len(results) < 10:
            return {'error': 'insufficient_data'}

        predictions = np.array([r['prediction'] for r in results])
        actuals = np.array([r['actual'] for r in results])

        mae = np.mean(np.abs(predictions - actuals))
        rmse = np.sqrt(np.mean((predictions - actuals) ** 2))
        mape = np.mean(np.abs((actuals - predictions) / actuals)) * 100

        return {
            'mae': float(mae),
            'rmse': float(rmse),
            'mape': float(mape),
            'sample_size': len(results)
        }

    def detect_drift(
        self,
        model_type: str,
        restaurant_id: int,
        threshold: float = 0.2
    ) -> Dict:
        """Detect model drift."""
        # Get training metrics
        training_metrics = self._get_training_metrics(model_type, restaurant_id)

        # Get recent production metrics
        recent_metrics = self.calculate_recent_accuracy(
            model_type,
            restaurant_id,
            days=7
        )

        if 'error' in recent_metrics:
            return {'drift_detected': False, 'reason': recent_metrics['error']}

        # Compare MAE
        training_mae = training_metrics.get('mae', 0)
        recent_mae = recent_metrics['mae']

        degradation = (recent_mae - training_mae) / training_mae
        drift_detected = degradation > threshold

        return {
            'drift_detected': drift_detected,
            'training_mae': training_mae,
            'recent_mae': recent_mae,
            'degradation_pct': degradation * 100,
            'threshold_pct': threshold * 100
        }

    def _get_training_metrics(
        self,
        model_type: str,
        restaurant_id: int
    ) -> Dict:
        """Get metrics from model training."""
        import json
        from pathlib import Path

        metadata_path = Path(f'models/{model_type}/restaurant_{restaurant_id}/latest/metadata.json')

        if not metadata_path.exists():
            return {}

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        return metadata.get('metrics', {})
```

### 3. System Resource Metrics

**Metrics**:

- CPU usage (%)
- Memory usage (MB)
- Disk I/O
- Network I/O
- Database connections

**Node Exporter** (for system metrics):

```yaml
# docker-compose.monitoring.yml
services:
  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - '9100:9100'
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
```

## Grafana Dashboards

### ML API Dashboard

**File**: `monitoring/grafana-dashboards/ml-api-dashboard.json`

```json
{
  "dashboard": {
    "title": "ML API Performance",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(ml_api_requests_total[5m])"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Response Time (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, ml_api_request_duration_seconds_bucket)"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(ml_api_requests_total{status=~\"5..\"}[5m])"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Cache Hit Rate",
        "targets": [
          {
            "expr": "rate(ml_cache_hits_total[5m]) / rate(ml_api_requests_total[5m])"
          }
        ],
        "type": "gauge"
      }
    ]
  }
}
```

### Model Performance Dashboard

```json
{
  "dashboard": {
    "title": "ML Model Performance",
    "panels": [
      {
        "title": "Prediction Count by Model",
        "targets": [
          {
            "expr": "rate(ml_predictions_total[5m])"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Model Accuracy (MAE)",
        "targets": [
          {
            "expr": "ml_model_mae"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Active Models",
        "targets": [
          {
            "expr": "ml_active_models"
          }
        ],
        "type": "stat"
      }
    ]
  }
}
```

## Alerting

### Alert Rules

**File**: `monitoring/alert-rules.yml`

```yaml
groups:
  - name: ml_api_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(ml_api_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: 'High error rate detected'
          description: 'Error rate is {{ $value }} (threshold: 0.05)'

      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, ml_api_request_duration_seconds_bucket) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: 'Slow API response time'
          description: 'P95 response time is {{ $value }}s (threshold: 5s)'

      - alert: LowCacheHitRate
        expr: rate(ml_cache_hits_total[5m]) / rate(ml_api_requests_total[5m]) < 0.5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: 'Low cache hit rate'
          description: 'Cache hit rate is {{ $value }} (threshold: 0.5)'

  - name: ml_model_alerts
    interval: 1h
    rules:
      - alert: ModelDriftDetected
        expr: ml_model_drift_detected == 1
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: 'Model drift detected'
          description: 'Model {{ $labels.model_type }} for restaurant {{ $labels.restaurant_id }} has drifted'

      - alert: ModelAccuracyDegraded
        expr: ml_model_mae > ml_model_training_mae * 1.5
        for: 2h
        labels:
          severity: critical
        annotations:
          summary: 'Model accuracy degraded'
          description: 'Model MAE is {{ $value }}, 50% worse than training'
```

### Alert Notifications

**Slack Integration**:

```python
# src/monitoring/alerting.py
import requests
import logging

logger = logging.getLogger(__name__)

class AlertManager:
    """Send alerts to various channels."""

    def __init__(self, slack_webhook_url: str):
        self.slack_webhook = slack_webhook_url

    def send_slack_alert(
        self,
        title: str,
        message: str,
        severity: str = 'warning'
    ):
        """Send alert to Slack."""
        color = {
            'info': '#36a64f',
            'warning': '#ff9900',
            'critical': '#ff0000'
        }.get(severity, '#808080')

        payload = {
            'attachments': [
                {
                    'color': color,
                    'title': title,
                    'text': message,
                    'footer': 'ML Service',
                    'ts': int(time.time())
                }
            ]
        }

        try:
            response = requests.post(
                self.slack_webhook,
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            logger.info(f"Slack alert sent: {title}")
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")

    def send_model_drift_alert(
        self,
        model_type: str,
        restaurant_id: int,
        drift_info: Dict
    ):
        """Send model drift alert."""
        title = f"🚨 Model Drift Detected: {model_type}"
        message = (
            f"Restaurant ID: {restaurant_id}\n"
            f"Training MAE: {drift_info['training_mae']:.2f}\n"
            f"Recent MAE: {drift_info['recent_mae']:.2f}\n"
            f"Degradation: {drift_info['degradation_pct']:.1f}%\n"
            f"Action: Model retraining recommended"
        )

        self.send_slack_alert(title, message, severity='warning')
```

## Logging

### Structured Logging

**File**: `src/utils/logging_config.py`

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Format logs as JSON."""

    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        if hasattr(record, 'extra'):
            log_data.update(record.extra)

        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)

def setup_logging(log_level='INFO'):
    """Setup logging configuration."""
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler('logs/ml-service.log')
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)

    return logger
```

### Log Aggregation

**ELK Stack Configuration**:

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
      - 'ES_JAVA_OPTS=-Xms512m -Xmx512m'
    ports:
      - '9200:9200'
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.5.0
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
    ports:
      - '5000:5000'
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.5.0
    ports:
      - '5601:5601'
    depends_on:
      - elasticsearch

volumes:
  elasticsearch-data:
```

## Maintenance Tasks

### Daily Tasks

```bash
#!/bin/bash
# scripts/daily_maintenance.sh

# Check model performance
python scripts/check_model_performance.py

# Clean old logs (keep 30 days)
find logs/ -name "*.log" -mtime +30 -delete

# Backup models
python scripts/backup_models.sh

# Check disk space
df -h | grep -E "/$|/app"
```

### Weekly Tasks

```bash
#!/bin/bash
# scripts/weekly_maintenance.sh

# Retrain models if drift detected
python scripts/check_and_retrain.py

# Clean old model versions (keep last 10)
python scripts/cleanup_old_models.py

# Generate performance report
python scripts/generate_performance_report.py

# Database maintenance
python scripts/vacuum_prediction_logs.py
```

### Monthly Tasks

```bash
#!/bin/bash
# scripts/monthly_maintenance.sh

# Full model retraining
python scripts/train_all_models.py

# Archive old prediction logs
python scripts/archive_old_logs.py

# System health check
python scripts/system_health_check.py

# Generate monthly report
python scripts/generate_monthly_report.py
```

## Performance Optimization

### Model Loading Optimization

```python
# src/services/model_loader.py
from functools import lru_cache
import joblib
from pathlib import Path

class ModelLoader:
    """Optimized model loading with caching."""

    def __init__(self):
        self._cache = {}

    @lru_cache(maxsize=10)
    def load_model(self, model_type: str, restaurant_id: int):
        """Load model with LRU cache."""
        cache_key = f"{model_type}:{restaurant_id}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        model_path = Path(f'models/{model_type}/restaurant_{restaurant_id}/latest/model.joblib')
        model = joblib.load(model_path)

        self._cache[cache_key] = model
        return model

    def unload_model(self, model_type: str, restaurant_id: int):
        """Unload model from cache."""
        cache_key = f"{model_type}:{restaurant_id}"
        if cache_key in self._cache:
            del self._cache[cache_key]
```

### Database Query Optimization

```python
# Use connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    db_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

# Use indexes
CREATE INDEX idx_prediction_logs_created_at ON ml_prediction_logs(created_at);
CREATE INDEX idx_prediction_logs_model_restaurant ON ml_prediction_logs(model_type, restaurant_id);
```

## Troubleshooting Guide

### Common Issues

**1. High Memory Usage**:

```bash
# Check memory usage
free -h

# Identify memory-heavy processes
ps aux --sort=-%mem | head -10

# Solution: Unload unused models
python scripts/unload_unused_models.py
```

**2. Slow Predictions**:

```bash
# Check model loading time
time python -c "import joblib; joblib.load('models/.../model.joblib')"

# Solution: Use model compression
python scripts/compress_models.py
```

**3. Model Drift**:

```bash
# Check drift status
python scripts/check_model_drift.py

# Solution: Retrain model
RESTAURANT_ID=1 python scripts/train_demand_model.py
```

---

**Next**: [Security & Privacy](./09-SECURITY.md)

# ML Service for Restaurant Management System - Project Summary

## Executive Summary

This document provides a high-level overview of the Machine Learning service designed to enhance the Restaurant Management System (RMS) with predictive analytics capabilities.

## Project Goals

1. **Demand Forecasting**: Predict order volume and item demand to optimize inventory and staffing
2. **Kitchen Optimization**: Estimate preparation times and identify bottlenecks
3. **Customer Intelligence**: Predict churn and lifetime value for targeted retention
4. **Inventory Management**: Optimize stock levels and reduce waste
5. **Dynamic Pricing**: Revenue optimization through demand-based pricing (future)

## Architecture Overview

### Separation of Concerns

The ML service runs as a **completely separate server** from the RMS:

```
RMS Server (Django)          ML Server (FastAPI)
    ↓                             ↓
PostgreSQL ←──────────────→ Read-Only Access
    ↓                             ↓
Redis Cache ←─────────────→ Shared Cache (Optional)
    ↓                             ↓
Dashboard ←────REST API────→ Predictions
```

### Key Benefits

- **Independent Scaling**: Scale ML service based on prediction load
- **Technology Flexibility**: Use ML-specific tools without affecting RMS
- **Fault Isolation**: ML service issues don't impact core RMS operations
- **Resource Optimization**: Dedicated resources for compute-intensive ML tasks

## Core ML Models

### 1. Demand Forecasting

- **Algorithm**: XGBoost + Prophet ensemble
- **Prediction**: Order volume by hour/day/week
- **Accuracy Target**: MAE < 5 orders/hour, R² > 0.85
- **Update Frequency**: Daily training

### 2. Kitchen Performance

- **Algorithm**: LightGBM
- **Prediction**: Preparation time per item/station
- **Accuracy Target**: MAE < 2 minutes, 80% within 5 minutes
- **Update Frequency**: Daily training

### 3. Customer Churn

- **Algorithm**: XGBoost Classifier
- **Prediction**: Probability of customer churn
- **Accuracy Target**: F1 > 0.67, AUC-ROC > 0.80
- **Update Frequency**: Weekly training

### 4. Customer Lifetime Value

- **Algorithm**: Random Forest Regressor
- **Prediction**: 12-month revenue per customer
- **Accuracy Target**: MAE < 20% of average LTV
- **Update Frequency**: Weekly training

### 5. Inventory Optimization

- **Algorithm**: Time Series + Optimization
- **Prediction**: Optimal reorder points and quantities
- **Accuracy Target**: Stockout rate < 5%, excess inventory < 15%
- **Update Frequency**: Weekly training

## Data Sources

The ML service reads from RMS database tables:

- **orders_order**: Order history, timestamps, totals
- **orders_orderitem**: Item details, quantities, modifiers
- **kitchen_orderitemstation**: Kitchen timing data
- **crm_customerprofile**: Customer demographics, loyalty
- **inventory_inventoryitem**: Stock levels, consumption
- **inventory_batch**: FIFO batch tracking
- **payments_payment**: Payment methods, amounts

## Technology Stack

### ML Libraries

- **scikit-learn**: Classical ML algorithms
- **XGBoost/LightGBM**: Gradient boosting
- **Prophet**: Time-series forecasting
- **pandas/numpy**: Data manipulation

### API Framework

- **FastAPI**: High-performance async API
- **Pydantic**: Data validation
- **uvicorn**: ASGI server

### Infrastructure

- **PostgreSQL**: RMS data source (read-only)
- **Redis**: Prediction caching
- **Docker**: Containerization
- **Prometheus/Grafana**: Monitoring

## Integration with RMS

### API Endpoints

```
GET  /api/predictions/demand
GET  /api/predictions/demand/items
POST /api/predictions/kitchen/prep-time
GET  /api/predictions/customer/churn/{id}
GET  /api/predictions/customer/ltv/{id}
GET  /api/predictions/inventory/reorder
GET  /api/predictions/inventory/stock-forecast
GET  /api/health
```

### Authentication

- API key authentication
- Restaurant-level access control
- Rate limiting (1000 requests/hour)

### Response Format

```json
{
  "success": true,
  "data": {
    // Prediction data
  },
  "metadata": {
    "model_version": "20260219_100000",
    "prediction_time_ms": 45,
    "cached": false
  }
}
```

## Deployment Options

### 1. Docker Compose (Development/Staging)

- Simple setup with docker-compose.yml
- Includes API server, training worker, Redis
- Suitable for single-server deployments

### 2. Kubernetes (Production)

- Horizontal scaling with multiple API pods
- Auto-scaling based on CPU/memory
- High availability with load balancing

### 3. AWS EC2 (Traditional)

- EC2 instance with systemd services
- Nginx reverse proxy with SSL
- Suitable for moderate scale

### 4. AWS ECS/Fargate (Serverless)

- Managed container orchestration
- Auto-scaling without server management
- Cost-effective for variable load

## Security Measures

- **Read-Only Database Access**: ML service cannot modify RMS data
- **API Authentication**: API keys with restaurant-level permissions
- **SSL/TLS Encryption**: All connections encrypted
- **Rate Limiting**: Prevent abuse and ensure fair usage
- **Input Validation**: Pydantic models validate all requests
- **Audit Logging**: Track all data access and predictions
- **GDPR Compliance**: Data anonymization and retention policies

## Monitoring & Maintenance

### Key Metrics

- API performance (response time, error rate)
- Model accuracy (MAE, RMSE, R²)
- System resources (CPU, memory, disk)
- Cache hit rate
- Prediction volume

### Alerting

- High error rate (> 5%)
- Slow response time (> 5s)
- Model drift detected
- Low cache hit rate (< 50%)

### Maintenance Schedule

- **Daily**: Model training, log cleanup
- **Weekly**: Customer model training, performance review
- **Monthly**: Full retraining, system health check

## Performance Expectations

### API Response Times

- Cached predictions: < 50ms
- Fresh predictions: < 500ms
- Batch predictions: < 2s

### Model Training Times

- Demand model: 5-10 minutes
- Kitchen model: 3-5 minutes
- Customer models: 10-15 minutes

### Accuracy Improvements

- Demand forecasting: 20-30% improvement over simple averages
- Kitchen timing: 15-25% improvement over historical averages
- Customer insights: Enable proactive retention strategies

## Cost Considerations

### Infrastructure Costs (Monthly Estimates)

**Small Scale** (1-5 restaurants):

- EC2 t3.large: $60
- RDS read replica: $50
- Redis: $15
- Total: ~$125/month

**Medium Scale** (5-20 restaurants):

- EC2 t3.xlarge: $120
- RDS read replica: $100
- Redis: $30
- Total: ~$250/month

**Large Scale** (20+ restaurants):

- ECS Fargate (3 tasks): $200
- RDS read replica: $200
- ElastiCache: $50
- Load Balancer: $20
- Total: ~$470/month

### ROI Potential

**Inventory Optimization**:

- 10-15% reduction in waste
- 5-10% reduction in stockouts
- Estimated savings: $500-2000/month per restaurant

**Demand Forecasting**:

- 10-20% improvement in staff scheduling
- 5-10% reduction in food waste
- Estimated savings: $300-1000/month per restaurant

**Customer Retention**:

- 5-10% reduction in churn
- 15-25% increase in customer lifetime value
- Estimated revenue impact: $1000-5000/month per restaurant

## Implementation Timeline

### Phase 1: Foundation (Weeks 1-2)

- Set up ML service infrastructure
- Implement data extraction pipelines
- Create model training framework
- Deploy basic API

### Phase 2: Core Models (Weeks 3-4)

- Demand forecasting model
- Kitchen performance model
- Basic inventory recommendations

### Phase 3: Customer Intelligence (Weeks 5-6)

- Customer churn prediction
- Lifetime value estimation
- Integration with CRM

### Phase 4: Advanced Features (Weeks 7-8)

- Dynamic pricing (optional)
- Multi-location optimization
- A/B testing framework

### Phase 5: Production Hardening (Weeks 9-10)

- Performance optimization
- Comprehensive monitoring
- Documentation and training

## Success Metrics

### Technical Metrics

- API uptime: > 99.5%
- Average response time: < 500ms
- Model accuracy: Meet or exceed targets
- Cache hit rate: > 70%

### Business Metrics

- Inventory waste reduction: 10-15%
- Stockout reduction: 20-30%
- Customer retention improvement: 5-10%
- Staff scheduling efficiency: 10-20%

## Risks & Mitigation

### Risk 1: Insufficient Historical Data

- **Mitigation**: Start with restaurants having 6+ months of data
- **Fallback**: Use rule-based predictions until sufficient data

### Risk 2: Model Drift

- **Mitigation**: Automated drift detection and retraining
- **Monitoring**: Weekly accuracy checks

### Risk 3: Integration Complexity

- **Mitigation**: Well-documented API, client libraries
- **Support**: Dedicated integration support

### Risk 4: Performance Issues

- **Mitigation**: Caching, horizontal scaling, optimization
- **Monitoring**: Real-time performance tracking

## Next Steps

1. **Review Documentation**: Read through all 10 documentation files
2. **Set Up Development Environment**: Follow Development Guide
3. **Deploy Staging Environment**: Use Docker Compose setup
4. **Train Initial Models**: Start with one restaurant
5. **Integrate with RMS**: Implement API client
6. **Test Predictions**: Validate accuracy with real data
7. **Deploy to Production**: Follow Deployment Guide
8. **Monitor Performance**: Set up Grafana dashboards
9. **Iterate and Improve**: Continuous model refinement

## Support & Resources

### Documentation

- [Architecture Overview](./01-ARCHITECTURE.md)
- [Data Pipeline](./02-DATA-PIPELINE.md)
- [ML Models](./03-ML-MODELS.md)
- [API Reference](./04-API-REFERENCE.md)
- [Deployment Guide](./05-DEPLOYMENT.md)
- [Integration Guide](./06-INTEGRATION.md)
- [Model Training](./07-MODEL-TRAINING.md)
- [Monitoring & Maintenance](./08-MONITORING.md)
- [Security & Privacy](./09-SECURITY.md)
- [Development Guide](./10-DEVELOPMENT.md)

### Contact

- Technical Lead: [Your Name]
- Email: [your-email@domain.com]
- Slack: #ml-service
- GitHub: [repository-url]

---

**Version**: 1.0.0  
**Last Updated**: February 19, 2026  
**Status**: Ready for Implementation

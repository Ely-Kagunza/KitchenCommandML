# Restaurant Management System - ML Service Documentation

## Overview

This documentation covers the Machine Learning service designed to provide predictive analytics for the Restaurant Management System (RMS). The ML service runs as a separate, independent server that reads data from the RMS database and provides predictions via REST API.

## Table of Contents

1. [Architecture Overview](./01-ARCHITECTURE.md)
2. [Data Pipeline](./02-DATA-PIPELINE.md)
3. [ML Models](./03-ML-MODELS.md)
4. [API Reference](./04-API-REFERENCE.md)
5. [Deployment Guide](./05-DEPLOYMENT.md)
6. [Integration Guide](./06-INTEGRATION.md)
7. [Model Training](./07-MODEL-TRAINING.md)
8. [Monitoring & Maintenance](./08-MONITORING.md)
9. [Security & Privacy](./09-SECURITY.md)
10. [Development Guide](./10-DEVELOPMENT.md)

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL access to RMS database (read-only)
- Redis (for caching)
- Docker (optional, for containerized deployment)

### Installation

```bash
# Clone the ML service repository
git clone <ml-service-repo>
cd ml-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your RMS database credentials

# Run the API server
uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

### Quick Test

```bash
# Health check
curl http://localhost:8000/api/health

# Get demand forecast
curl http://localhost:8000/api/predictions/demand?restaurant_id=1&hours=24
```

## Key Features

### 1. Demand Forecasting

- Predict order volume by hour/day/week
- Item-level demand predictions
- Category-level forecasting
- Seasonal pattern detection

### 2. Inventory Optimization

- Stock level recommendations
- Reorder point optimization
- Expiry prediction
- Waste reduction insights

### 3. Kitchen Performance

- Prep time estimation per item/station
- Bottleneck detection
- Staff productivity analysis
- Queue time predictions

### 4. Customer Analytics

- Churn prediction
- Lifetime value estimation
- Repeat purchase probability
- Loyalty tier progression forecasting

### 5. Dynamic Pricing (Advanced)

- Demand-based pricing recommendations
- Inventory clearance pricing
- Happy hour optimization
- Competitor price analysis

## Architecture Principles

### Separation of Concerns

- **RMS Server**: Handles all business logic, transactions, user management
- **ML Server**: Focuses solely on predictions and analytics
- **Communication**: REST API calls from RMS to ML server

### Data Flow

```
RMS PostgreSQL → ML Data Pipeline → Feature Engineering → Model Training
                                                              ↓
RMS Dashboard ← REST API ← Prediction Service ← Trained Models
```

### Scalability

- Horizontal scaling of API servers
- Async model training
- Prediction caching
- Model versioning

## Technology Stack

### Core ML Libraries

- **scikit-learn**: Classical ML algorithms
- **XGBoost/LightGBM**: Gradient boosting models
- **Prophet**: Time-series forecasting
- **pandas/numpy**: Data manipulation
- **joblib**: Model serialization

### API Framework

- **FastAPI**: High-performance async API
- **Pydantic**: Data validation
- **uvicorn**: ASGI server

### Data & Caching

- **SQLAlchemy**: Database ORM
- **Redis**: Prediction caching
- **PostgreSQL**: RMS data source (read-only)

### Deployment

- **Docker**: Containerization
- **Docker Compose**: Local orchestration
- **Kubernetes**: Production orchestration (optional)

## Project Structure

```
ml-service/
├── src/
│   ├── api/              # FastAPI application
│   ├── models/           # Trained model storage
│   ├── pipelines/        # Data extraction & processing
│   ├── training/         # Model training scripts
│   ├── services/         # Prediction services
│   └── utils/            # Utilities
├── notebooks/            # Jupyter notebooks for analysis
├── tests/                # Unit and integration tests
├── docker/               # Docker configuration
├── scripts/              # Training and deployment scripts
└── docs/                 # This documentation
```

## Support & Contributing

### Getting Help

- Check the documentation in this folder
- Review the API reference for endpoint details
- Check logs in `logs/` directory

### Reporting Issues

- Document the issue with reproduction steps
- Include relevant logs and error messages
- Specify RMS version and ML service version

### Contributing

- Follow the development guide
- Write tests for new features
- Update documentation
- Follow code style guidelines

## License

[Your License Here]

## Version History

- **v1.0.0** (2026-02-19): Initial release
  - Demand forecasting
  - Kitchen performance predictions
  - Basic inventory optimization
  - Customer analytics

---

**Next Steps**: Read the [Architecture Overview](./01-ARCHITECTURE.md) to understand the system design.

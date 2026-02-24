# Architecture Overview

## System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                     Restaurant Management System                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Django     │  │  PostgreSQL  │  │    Redis     │          │
│  │   Backend    │  │   Database   │  │    Cache     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                   │
└─────────┼──────────────────┼──────────────────┼───────────────────┘
          │                  │                  │
          │ API Calls        │ Read-Only        │ Shared Cache
          │                  │ Connection       │ (Optional)
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                        ML Service                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   FastAPI    │  │ Data Pipeline│  │Model Training│          │
│  │   REST API   │  │   Service    │  │   Service    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                   │
│         │                  │                  │                   │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐          │
│  │ Prediction   │  │   Feature    │  │   Trained    │          │
│  │   Service    │  │ Engineering  │  │   Models     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. FastAPI REST API

**Purpose**: Expose ML predictions via HTTP endpoints

**Responsibilities**:

- Handle incoming prediction requests
- Validate request parameters
- Route to appropriate prediction service
- Return formatted responses
- Handle errors gracefully

**Technology**: FastAPI, Pydantic, uvicorn

**Endpoints**:

- `/api/predictions/demand`
- `/api/predictions/kitchen`
- `/api/predictions/customer`
- `/api/predictions/inventory`
- `/api/health`
- `/api/models/info`

### 2. Data Pipeline Service

**Purpose**: Extract and transform data from RMS database

**Responsibilities**:

- Connect to RMS PostgreSQL (read-only)
- Query historical data
- Clean and validate data
- Handle missing values
- Aggregate data for features
- Cache processed data

**Key Modules**:

- `data_extractor.py`: SQL queries to RMS DB
- `data_processor.py`: Data cleaning and validation
- `feature_engineering.py`: Create ML features

**Data Sources**:

- Orders table (order history, timestamps, totals)
- OrderItems table (item details, quantities, modifiers)
- OrderItemStation table (kitchen timing data)
- CustomerProfile table (customer demographics, loyalty)
- InventoryItem & Batch tables (stock levels, consumption)
- Payment table (payment methods, amounts, timing)

### 3. Model Training Service

**Purpose**: Train and update ML models

**Responsibilities**:

- Load historical data
- Split train/test datasets
- Train models with hyperparameter tuning
- Evaluate model performance
- Version and save models
- Log training metrics

**Training Schedule**:

- **Daily**: Kitchen performance, demand forecasting
- **Weekly**: Customer analytics, inventory optimization
- **Monthly**: Pricing optimization, full retraining

**Model Storage**:

```
models/
├── demand_forecasting/
│   ├── v1.0.0/
│   │   ├── model.joblib
│   │   ├── scaler.joblib
│   │   ├── metadata.json
│   │   └── metrics.json
│   └── latest -> v1.0.0
├── kitchen_performance/
│   └── ...
└── customer_analytics/
    └── ...
```

### 4. Prediction Service

**Purpose**: Generate predictions using trained models

**Responsibilities**:

- Load trained models
- Prepare input features
- Generate predictions
- Post-process results
- Cache predictions
- Handle model fallbacks

**Services**:

- `demand_service.py`: Demand forecasting
- `kitchen_service.py`: Kitchen performance
- `customer_service.py`: Customer analytics
- `inventory_service.py`: Inventory optimization

### 5. Caching Layer

**Purpose**: Improve response times and reduce computation

**Strategy**:

- Cache predictions with TTL (Time To Live)
- Cache processed features
- Cache model metadata
- Invalidate on data updates

**Redis Keys**:

```
ml:prediction:demand:{restaurant_id}:{date}
ml:prediction:kitchen:{station_id}:{item_id}
ml:prediction:customer:{customer_id}
ml:features:{entity_type}:{entity_id}
ml:model:metadata:{model_name}
```

**TTL Settings**:

- Demand predictions: 1 hour
- Kitchen predictions: 30 minutes
- Customer predictions: 24 hours
- Feature cache: 6 hours

## Communication Patterns

### Pattern 1: Synchronous API Call (Recommended)

```
RMS Dashboard → HTTP GET → ML API → Prediction Service → Response
                                    ↓
                                  Cache
```

**Use Cases**:

- Real-time dashboard widgets
- On-demand predictions
- User-triggered forecasts

**Pros**:

- Simple implementation
- Immediate results
- Easy debugging

**Cons**:

- Latency dependent on ML service
- Requires timeout handling

### Pattern 2: Asynchronous Task Queue

```
RMS Celery Task → HTTP GET → ML API → Prediction Service
                                       ↓
                                    Response
                                       ↓
RMS Cache/DB ← Store Results ← Celery Task
```

**Use Cases**:

- Batch predictions
- Heavy computations
- Scheduled updates

**Pros**:

- Non-blocking
- Retry logic
- Better for heavy operations

**Cons**:

- More complex
- Delayed results

### Pattern 3: Webhook/Push (Advanced)

```
ML Service (Scheduled Job) → Train Model → Generate Predictions
                                            ↓
                                         HTTP POST
                                            ↓
                                    RMS Webhook Endpoint
                                            ↓
                                    Store in RMS DB/Cache
```

**Use Cases**:

- Proactive predictions
- Scheduled forecasts
- Batch updates

**Pros**:

- RMS doesn't need to poll
- Efficient for batch updates
- Decoupled timing

**Cons**:

- Requires webhook endpoint in RMS
- Authentication complexity
- Error handling

## Data Flow

### Training Flow

```
1. Scheduled Job Triggers
   ↓
2. Data Extractor queries RMS DB
   ↓
3. Data Processor cleans data
   ↓
4. Feature Engineering creates features
   ↓
5. Model Trainer trains model
   ↓
6. Model Evaluator validates performance
   ↓
7. Model Versioner saves model
   ↓
8. Metadata Logger records metrics
```

### Prediction Flow

```
1. RMS sends API request
   ↓
2. API validates parameters
   ↓
3. Check cache for existing prediction
   ↓
4. If cache miss:
   a. Load trained model
   b. Extract features
   c. Generate prediction
   d. Cache result
   ↓
5. Return formatted response
```

## Scalability Considerations

### Horizontal Scaling

**API Servers**:

- Run multiple FastAPI instances
- Load balancer distributes requests
- Stateless design (no session storage)

**Model Training**:

- Separate training workers
- Queue-based job distribution
- Parallel training for different models

### Vertical Scaling

**Memory**:

- Load models on-demand
- Unload unused models
- Use model compression

**CPU**:

- Multi-threaded predictions
- Batch prediction optimization
- GPU support for deep learning (future)

### Caching Strategy

**Levels**:

1. **L1**: In-memory cache (per API instance)
2. **L2**: Redis cache (shared across instances)
3. **L3**: Pre-computed predictions (database)

**Cache Invalidation**:

- Time-based (TTL)
- Event-based (on data updates)
- Manual (admin trigger)

## Fault Tolerance

### Model Fallbacks

```python
1. Try latest model version
   ↓ (if fails)
2. Try previous stable version
   ↓ (if fails)
3. Use rule-based fallback
   ↓ (if fails)
4. Return default/average values
```

### Database Connection

- Connection pooling
- Automatic reconnection
- Read replica support
- Query timeout handling

### API Resilience

- Request timeout (30s default)
- Circuit breaker pattern
- Graceful degradation
- Health check endpoint

## Security Architecture

### Network Security

```
Internet → Firewall → Load Balancer → ML API Servers
                                       ↓
                                    Private Network
                                       ↓
                                    RMS Database (read-only)
```

### Authentication

- API key authentication
- JWT token support (optional)
- Rate limiting per client
- IP whitelisting (optional)

### Data Security

- Read-only database user
- Encrypted connections (SSL/TLS)
- No PII in logs
- Data anonymization (where applicable)

## Monitoring Architecture

### Metrics Collection

```
ML Service → Prometheus Exporter → Prometheus Server → Grafana Dashboard
              ↓
           Logs → ELK Stack / CloudWatch
              ↓
           Traces → Jaeger / DataDog
```

### Key Metrics

**API Metrics**:

- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (%)
- Cache hit rate (%)

**Model Metrics**:

- Prediction accuracy
- Model drift detection
- Feature importance changes
- Training time

**System Metrics**:

- CPU usage
- Memory usage
- Disk I/O
- Network I/O

## Deployment Architecture

### Development Environment

```
Developer Machine
├── ML Service (localhost:8000)
├── RMS DB (localhost:5432)
└── Redis (localhost:6379)
```

### Staging Environment

```
Staging Server
├── ML API (Docker container)
├── ML Training Worker (Docker container)
├── Redis (Docker container)
└── RMS DB (shared staging DB)
```

### Production Environment

```
Production Cluster
├── Load Balancer
├── ML API Servers (3+ instances)
├── ML Training Workers (2+ instances)
├── Redis Cluster (HA setup)
├── Model Storage (S3/GCS)
└── RMS DB (read replica)
```

## Technology Decisions

### Why FastAPI?

- High performance (async support)
- Automatic API documentation
- Type validation with Pydantic
- Easy to test and deploy

### Why Separate Server?

- Independent scaling
- Technology flexibility
- Fault isolation
- Resource optimization

### Why Redis?

- Fast in-memory caching
- Pub/sub support (future)
- Shared cache across instances
- TTL support

### Why Read-Only DB Access?

- Security (no accidental writes)
- Performance (no transaction locks)
- Isolation (ML doesn't affect RMS)
- Compliance (audit trail)

## Future Enhancements

### Phase 2

- Real-time streaming predictions
- Deep learning models
- Multi-model ensembles
- A/B testing framework

### Phase 3

- AutoML for model selection
- Federated learning (multi-tenant)
- Edge deployment (on-premise)
- Mobile SDK

---

**Next**: [Data Pipeline](./02-DATA-PIPELINE.md)

# Deployment Guide

## Overview

This guide covers deploying the ML service in various environments, from local development to production.

## Prerequisites

### System Requirements

**Minimum**:

- CPU: 2 cores
- RAM: 4 GB
- Disk: 20 GB
- OS: Linux (Ubuntu 20.04+), macOS, Windows with WSL2

**Recommended (Production)**:

- CPU: 4+ cores
- RAM: 8+ GB
- Disk: 50+ GB SSD
- OS: Linux (Ubuntu 22.04 LTS)

### Software Requirements

- Python 3.9+
- PostgreSQL 13+ (RMS database access)
- Redis 6+
- Docker 20+ (optional)
- Docker Compose 2+ (optional)

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourorg/ml-service.git
cd ml-service
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:

```bash
# RMS Database (Read-Only)
RMS_DB_URL=postgresql://ml_readonly:password@localhost:5432/rms_db

# Redis
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
LOG_LEVEL=INFO

# Security
API_KEY_SECRET=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Model Storage
MODEL_STORAGE_PATH=./models
MODEL_CACHE_TTL=3600

# Feature Flags
ENABLE_CACHING=true
ENABLE_MONITORING=true
```

### 5. Create Read-Only Database User

Connect to RMS PostgreSQL and run:

```sql
-- Create read-only user
CREATE USER ml_readonly WITH PASSWORD 'secure_password_here';

-- Grant connect permission
GRANT CONNECT ON DATABASE rms_db TO ml_readonly;

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO ml_readonly;

-- Grant select on all tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ml_readonly;

-- Grant select on future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO ml_readonly;

-- Set default transaction to read-only
ALTER USER ml_readonly SET default_transaction_read_only = on;
```

### 6. Initialize Database Schema (Optional)

If using a separate ML database for logs/metadata:

```bash
python scripts/init_db.py
```

### 7. Run Development Server

```bash
# Start API server
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

# Or use the development script
python scripts/run_dev.py
```

### 8. Verify Installation

```bash
# Health check
curl http://localhost:8000/api/health

# Test prediction (requires trained model)
curl -H "Authorization: Bearer test_key" \
     "http://localhost:8000/api/predictions/demand?restaurant_id=1&hours=24"
```

## Docker Deployment

### Docker Compose (Recommended for Development/Staging)

**File**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  ml-api:
    build:
      context: .
      dockerfile: docker/Dockerfile
    container_name: ml-api
    ports:
      - '8000:8000'
    environment:
      - RMS_DB_URL=postgresql://ml_readonly:${DB_PASSWORD}@rms-db:5432/rms_db
      - REDIS_URL=redis://redis:6379/0
      - API_WORKERS=4
      - LOG_LEVEL=INFO
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    depends_on:
      - redis
    restart: unless-stopped
    networks:
      - ml-network

  ml-trainer:
    build:
      context: .
      dockerfile: docker/Dockerfile
    container_name: ml-trainer
    command: python scripts/schedule_training.py
    environment:
      - RMS_DB_URL=postgresql://ml_readonly:${DB_PASSWORD}@rms-db:5432/rms_db
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    depends_on:
      - redis
    restart: unless-stopped
    networks:
      - ml-network

  redis:
    image: redis:7-alpine
    container_name: ml-redis
    ports:
      - '6379:6379'
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - ml-network

volumes:
  redis-data:

networks:
  ml-network:
    driver: bridge
```

**File**: `docker/Dockerfile`

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY models/ ./models/

# Create non-root user
RUN useradd -m -u 1000 mluser && \
    chown -R mluser:mluser /app

USER mluser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')"

# Run application
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Build and Run

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f ml-api

# Stop services
docker-compose down
```

## Production Deployment

### Option 1: Kubernetes

**File**: `k8s/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-api
  namespace: ml-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-api
  template:
    metadata:
      labels:
        app: ml-api
    spec:
      containers:
        - name: ml-api
          image: yourregistry/ml-service:latest
          ports:
            - containerPort: 8000
          env:
            - name: RMS_DB_URL
              valueFrom:
                secretKeyRef:
                  name: ml-secrets
                  key: rms-db-url
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: ml-secrets
                  key: redis-url
            - name: API_WORKERS
              value: '4'
          resources:
            requests:
              memory: '2Gi'
              cpu: '1000m'
            limits:
              memory: '4Gi'
              cpu: '2000m'
          livenessProbe:
            httpGet:
              path: /api/health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /api/health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
          volumeMounts:
            - name: models
              mountPath: /app/models
      volumes:
        - name: models
          persistentVolumeClaim:
            claimName: ml-models-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: ml-api-service
  namespace: ml-service
spec:
  selector:
    app: ml-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ml-models-pvc
  namespace: ml-service
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 50Gi
  storageClassName: standard
```

**Deploy to Kubernetes**:

```bash
# Create namespace
kubectl create namespace ml-service

# Create secrets
kubectl create secret generic ml-secrets \
  --from-literal=rms-db-url='postgresql://...' \
  --from-literal=redis-url='redis://...' \
  -n ml-service

# Apply deployment
kubectl apply -f k8s/deployment.yaml

# Check status
kubectl get pods -n ml-service
kubectl get svc -n ml-service

# View logs
kubectl logs -f deployment/ml-api -n ml-service
```

### Option 2: AWS EC2

**1. Launch EC2 Instance**:

- Instance type: t3.large or larger
- OS: Ubuntu 22.04 LTS
- Security group: Allow ports 22 (SSH), 8000 (API)
- Storage: 50 GB SSD

**2. Install Dependencies**:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install PostgreSQL client
sudo apt install -y postgresql-client

# Install Redis
sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Install Docker (optional)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
```

**3. Deploy Application**:

```bash
# Clone repository
git clone https://github.com/yourorg/ml-service.git
cd ml-service

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit configuration

# Create systemd service
sudo nano /etc/systemd/system/ml-api.service
```

**File**: `/etc/systemd/system/ml-api.service`

```ini
[Unit]
Description=ML Service API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ml-service
Environment="PATH=/home/ubuntu/ml-service/venv/bin"
ExecStart=/home/ubuntu/ml-service/venv/bin/uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**4. Start Service**:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable ml-api

# Start service
sudo systemctl start ml-api

# Check status
sudo systemctl status ml-api

# View logs
sudo journalctl -u ml-api -f
```

**5. Setup Nginx Reverse Proxy**:

```bash
# Install Nginx
sudo apt install -y nginx

# Configure Nginx
sudo nano /etc/nginx/sites-available/ml-api
```

**File**: `/etc/nginx/sites-available/ml-api`

```nginx
server {
    listen 80;
    server_name ml-api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ml-api /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

**6. Setup SSL with Let's Encrypt**:

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d ml-api.yourdomain.com

# Auto-renewal is configured automatically
```

### Option 3: AWS ECS/Fargate

**1. Create ECR Repository**:

```bash
# Create repository
aws ecr create-repository --repository-name ml-service

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.us-east-1.amazonaws.com

# Build and push image
docker build -t ml-service -f docker/Dockerfile .
docker tag ml-service:latest \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/ml-service:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/ml-service:latest
```

**2. Create ECS Task Definition**:

```json
{
  "family": "ml-service",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "containerDefinitions": [
    {
      "name": "ml-api",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/ml-service:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "API_WORKERS",
          "value": "4"
        }
      ],
      "secrets": [
        {
          "name": "RMS_DB_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:ml-rms-db-url"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ml-service",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**3. Create ECS Service**:

```bash
aws ecs create-service \
  --cluster ml-cluster \
  --service-name ml-api \
  --task-definition ml-service \
  --desired-count 3 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=ml-api,containerPort=8000"
```

## Model Training Scheduler

### Cron-based Scheduling

**File**: `/etc/cron.d/ml-training`

```bash
# Daily demand model training at 2 AM
0 2 * * * ubuntu cd /home/ubuntu/ml-service && /home/ubuntu/ml-service/venv/bin/python scripts/train_demand_model.py >> /var/log/ml-training.log 2>&1

# Weekly customer analytics training on Sunday at 3 AM
0 3 * * 0 ubuntu cd /home/ubuntu/ml-service && /home/ubuntu/ml-service/venv/bin/python scripts/train_customer_models.py >> /var/log/ml-training.log 2>&1

# Daily kitchen performance training at 4 AM
0 4 * * * ubuntu cd /home/ubuntu/ml-service && /home/ubuntu/ml-service/venv/bin/python scripts/train_kitchen_model.py >> /var/log/ml-training.log 2>&1
```

### Celery-based Scheduling (Advanced)

**File**: `src/tasks/celery_app.py`

```python
from celery import Celery
from celery.schedules import crontab

app = Celery('ml_tasks', broker='redis://localhost:6379/0')

app.conf.beat_schedule = {
    'train-demand-model-daily': {
        'task': 'src.tasks.training.train_demand_model',
        'schedule': crontab(hour=2, minute=0),
    },
    'train-customer-models-weekly': {
        'task': 'src.tasks.training.train_customer_models',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),
    },
    'train-kitchen-model-daily': {
        'task': 'src.tasks.training.train_kitchen_model',
        'schedule': crontab(hour=4, minute=0),
    },
}
```

**Start Celery Worker and Beat**:

```bash
# Start worker
celery -A src.tasks.celery_app worker --loglevel=info

# Start beat scheduler
celery -A src.tasks.celery_app beat --loglevel=info
```

## Monitoring Setup

### Prometheus + Grafana

**File**: `docker-compose.monitoring.yml`

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - '9090:9090'
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    networks:
      - ml-network

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - '3000:3000'
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana-dashboards:/etc/grafana/provisioning/dashboards
    networks:
      - ml-network

volumes:
  prometheus-data:
  grafana-data:

networks:
  ml-network:
    external: true
```

**File**: `monitoring/prometheus.yml`

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ml-api'
    static_configs:
      - targets: ['ml-api:8000']
```

## Backup and Recovery

### Model Backup

```bash
#!/bin/bash
# scripts/backup_models.sh

BACKUP_DIR="/backups/ml-models"
MODEL_DIR="/app/models"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
tar -czf "$BACKUP_DIR/models_$DATE.tar.gz" "$MODEL_DIR"

# Upload to S3 (optional)
aws s3 cp "$BACKUP_DIR/models_$DATE.tar.gz" \
  s3://your-bucket/ml-models/

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "models_*.tar.gz" -mtime +7 -delete
```

### Database Backup (if using separate ML DB)

```bash
#!/bin/bash
# scripts/backup_db.sh

BACKUP_DIR="/backups/ml-db"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
pg_dump -h localhost -U ml_user ml_db | \
  gzip > "$BACKUP_DIR/ml_db_$DATE.sql.gz"

# Upload to S3
aws s3 cp "$BACKUP_DIR/ml_db_$DATE.sql.gz" \
  s3://your-bucket/ml-db/

# Keep only last 30 days
find "$BACKUP_DIR" -name "ml_db_*.sql.gz" -mtime +30 -delete
```

## Scaling Strategies

### Horizontal Scaling

**Load Balancer Configuration** (Nginx):

```nginx
upstream ml_api {
    least_conn;
    server ml-api-1:8000;
    server ml-api-2:8000;
    server ml-api-3:8000;
}

server {
    listen 80;
    server_name ml-api.yourdomain.com;

    location / {
        proxy_pass http://ml_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Auto-scaling (Kubernetes)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-api-hpa
  namespace: ml-service
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

## Troubleshooting

### Common Issues

**1. API not responding**:

```bash
# Check service status
sudo systemctl status ml-api

# Check logs
sudo journalctl -u ml-api -n 100

# Check port
sudo netstat -tlnp | grep 8000
```

**2. Database connection errors**:

```bash
# Test database connection
psql -h rms-db-host -U ml_readonly -d rms_db -c "SELECT 1;"

# Check network connectivity
ping rms-db-host
telnet rms-db-host 5432
```

**3. Model loading errors**:

```bash
# Check model files
ls -lh models/demand_forecasting/restaurant_1/latest/

# Verify model integrity
python -c "import joblib; model = joblib.load('models/.../model.joblib'); print('OK')"
```

---

**Next**: [Integration Guide](./06-INTEGRATION.md)

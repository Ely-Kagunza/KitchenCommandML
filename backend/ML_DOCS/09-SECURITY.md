# Security & Privacy

## Overview

Security and privacy are critical for ML services handling restaurant and customer data.

## Security Architecture

```
Internet → Firewall → Load Balancer → ML API (Auth) → Private Network → RMS DB (Read-Only)
```

## Authentication & Authorization

### API Key Authentication

**Implementation**:

```python
# src/api/auth.py
from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import hashlib
import hmac
from typing import Optional

security = HTTPBearer()

class APIKeyAuth:
    """API key authentication."""

    def __init__(self, valid_keys: dict):
        """
        Initialize with valid API keys.

        Args:
            valid_keys: Dict of {api_key: {restaurant_ids: [...], permissions: [...]}}
        """
        self.valid_keys = valid_keys

    async def verify_api_key(
        self,
        credentials: HTTPAuthorizationCredentials = Security(security)
    ) -> dict:
        """Verify API key and return context."""
        api_key = credentials.credentials

        # Hash the API key for comparison
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        if key_hash not in self.valid_keys:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )

        return self.valid_keys[key_hash]

    def check_restaurant_access(
        self,
        context: dict,
        restaurant_id: int
    ) -> bool:
        """Check if API key has access to restaurant."""
        allowed_restaurants = context.get('restaurant_ids', [])

        # Empty list means access to all restaurants
        if not allowed_restaurants:
            return True

        return restaurant_id in allowed_restaurants

# Usage in endpoints
@app.get('/api/predictions/demand')
async def get_demand_forecast(
    restaurant_id: int,
    context: dict = Depends(api_key_auth.verify_api_key)
):
    """Get demand forecast with auth."""
    if not api_key_auth.check_restaurant_access(context, restaurant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this restaurant"
        )

    # ... rest of endpoint logic
```

### JWT Token Authentication (Optional)

```python
# src/api/jwt_auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

async def verify_token(credentials = Security(security)):
    """Verify JWT token."""
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
```

## Database Security

### Read-Only Access

**Create Read-Only User**:

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

-- Revoke any write permissions (safety)
REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA public FROM ml_readonly;
```

### Connection Security

**SSL/TLS Configuration**:

```python
# src/database.py
from sqlalchemy import create_engine

# PostgreSQL with SSL
db_url = (
    f"postgresql://{user}:{password}@{host}:{port}/{database}"
    f"?sslmode=require"
)

engine = create_engine(
    db_url,
    connect_args={
        'sslmode': 'require',
        'sslrootcert': '/path/to/ca-cert.pem',
        'sslcert': '/path/to/client-cert.pem',
        'sslkey': '/path/to/client-key.pem'
    }
)
```

### Connection Pooling

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    db_url,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True  # Verify connections before use
)
```

## Data Privacy

### PII Handling

**Data Anonymization**:

```python
# src/utils/privacy.py
import hashlib
from typing import Optional

class DataAnonymizer:
    """Anonymize sensitive data."""

    @staticmethod
    def hash_pii(value: str, salt: str = '') -> str:
        """Hash PII data."""
        return hashlib.sha256(f"{value}{salt}".encode()).hexdigest()

    @staticmethod
    def mask_phone(phone: str) -> str:
        """Mask phone number."""
        if len(phone) < 4:
            return '****'
        return f"****{phone[-4:]}"

    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email address."""
        if '@' not in email:
            return '****'

        local, domain = email.split('@')
        if len(local) <= 2:
            masked_local = '**'
        else:
            masked_local = f"{local[0]}{'*' * (len(local) - 2)}{local[-1]}"

        return f"{masked_local}@{domain}"

    @staticmethod
    def anonymize_customer_data(customer: dict) -> dict:
        """Anonymize customer data for ML."""
        return {
            'customer_id': customer['id'],
            'phone_hash': DataAnonymizer.hash_pii(customer.get('phone', '')),
            'email_hash': DataAnonymizer.hash_pii(customer.get('email', '')),
            'age_group': DataAnonymizer.get_age_group(customer.get('birth_date')),
            # Keep non-PII data
            'total_orders': customer['total_orders'],
            'total_spent': customer['total_spent'],
            'loyalty_tier': customer['loyalty_tier']
        }

    @staticmethod
    def get_age_group(birth_date: Optional[str]) -> str:
        """Convert birth date to age group."""
        if not birth_date:
            return 'unknown'

        from datetime import datetime
        age = (datetime.now() - datetime.fromisoformat(birth_date)).days // 365

        if age < 18:
            return '0-17'
        elif age < 25:
            return '18-24'
        elif age < 35:
            return '25-34'
        elif age < 45:
            return '35-44'
        elif age < 55:
            return '45-54'
        elif age < 65:
            return '55-64'
        else:
            return '65+'
```

### GDPR Compliance

**Data Retention Policy**:

```python
# src/utils/data_retention.py
from datetime import datetime, timedelta

class DataRetentionPolicy:
    """Manage data retention for GDPR compliance."""

    # Retention periods
    PREDICTION_LOGS_DAYS = 90
    TRAINING_DATA_DAYS = 365
    MODEL_VERSIONS_COUNT = 10

    @staticmethod
    def cleanup_old_prediction_logs(db_connection):
        """Delete old prediction logs."""
        cutoff_date = datetime.now() - timedelta(days=DataRetentionPolicy.PREDICTION_LOGS_DAYS)

        db_connection.execute("""
            DELETE FROM ml_prediction_logs
            WHERE created_at < %s
        """, (cutoff_date,))

    @staticmethod
    def cleanup_old_models(model_dir: str):
        """Keep only recent model versions."""
        from pathlib import Path
        import shutil

        model_path = Path(model_dir)

        # Get all version directories
        versions = sorted(
            [d for d in model_path.iterdir() if d.is_dir() and d.name != 'latest'],
            key=lambda x: x.name,
            reverse=True
        )

        # Keep only recent versions
        for old_version in versions[DataRetentionPolicy.MODEL_VERSIONS_COUNT:]:
            shutil.rmtree(old_version)

    @staticmethod
    def anonymize_customer_data_for_training(customer_data):
        """Anonymize customer data before training."""
        anonymizer = DataAnonymizer()
        return [anonymizer.anonymize_customer_data(c) for c in customer_data]
```

**Right to be Forgotten**:

```python
# src/utils/gdpr.py
class GDPRCompliance:
    """GDPR compliance utilities."""

    @staticmethod
    def delete_customer_data(customer_id: int, db_connection):
        """Delete all customer data (right to be forgotten)."""
        # Delete prediction logs
        db_connection.execute("""
            DELETE FROM ml_prediction_logs
            WHERE features->>'customer_id' = %s
        """, (str(customer_id),))

        # Anonymize in training data cache
        db_connection.execute("""
            UPDATE ml_training_data_cache
            SET customer_data = jsonb_set(
                customer_data,
                '{customer_id}',
                to_jsonb(%s::text)
            )
            WHERE customer_data->>'customer_id' = %s
        """, (f'deleted_{customer_id}', str(customer_id)))

    @staticmethod
    def export_customer_data(customer_id: int, db_connection) -> dict:
        """Export all customer data (data portability)."""
        # Get prediction logs
        predictions = db_connection.query("""
            SELECT *
            FROM ml_prediction_logs
            WHERE features->>'customer_id' = %s
        """, (str(customer_id),))

        return {
            'customer_id': customer_id,
            'predictions': predictions,
            'exported_at': datetime.now().isoformat()
        }
```

## Network Security

### Firewall Rules

```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 8000/tcp  # ML API
sudo ufw enable
```

### SSL/TLS Configuration

**Nginx SSL Configuration**:

```nginx
server {
    listen 443 ssl http2;
    server_name ml-api.yourdomain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/ml-api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ml-api.yourdomain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name ml-api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## Rate Limiting

### API Rate Limiting

```python
# src/api/rate_limiting.py
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import redis

class RateLimiter:
    """Rate limiting for API endpoints."""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """Check if request is within rate limit."""
        current = self.redis.get(key)

        if current is None:
            # First request in window
            self.redis.setex(key, window_seconds, 1)
            return True

        current = int(current)

        if current >= max_requests:
            return False

        # Increment counter
        self.redis.incr(key)
        return True

    def get_remaining_requests(
        self,
        key: str,
        max_requests: int
    ) -> int:
        """Get remaining requests in current window."""
        current = self.redis.get(key)

        if current is None:
            return max_requests

        return max(0, max_requests - int(current))

# Middleware
@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    """Apply rate limiting."""
    # Get API key from header
    api_key = request.headers.get('Authorization', '').replace('Bearer ', '')

    if not api_key:
        return await call_next(request)

    # Rate limit key
    rate_limit_key = f"rate_limit:{api_key}:{datetime.now().strftime('%Y%m%d%H')}"

    # Check rate limit (1000 requests per hour)
    if not rate_limiter.check_rate_limit(rate_limit_key, 1000, 3600):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )

    response = await call_next(request)

    # Add rate limit headers
    remaining = rate_limiter.get_remaining_requests(rate_limit_key, 1000)
    response.headers['X-RateLimit-Limit'] = '1000'
    response.headers['X-RateLimit-Remaining'] = str(remaining)

    return response
```

## Input Validation

### Request Validation

```python
# src/api/validation.py
from pydantic import BaseModel, validator, Field
from typing import Optional, List

class DemandForecastRequest(BaseModel):
    """Demand forecast request validation."""

    restaurant_id: int = Field(..., gt=0, description="Restaurant ID")
    hours: int = Field(24, ge=1, le=168, description="Forecast hours")
    granularity: str = Field('hourly', regex='^(hourly|daily)$')

    @validator('restaurant_id')
    def validate_restaurant_id(cls, v):
        """Validate restaurant ID exists."""
        # Check if restaurant exists in database
        if not restaurant_exists(v):
            raise ValueError(f"Restaurant {v} not found")
        return v

class PrepTimeRequest(BaseModel):
    """Prep time prediction request validation."""

    restaurant_id: int = Field(..., gt=0)
    station_id: int = Field(..., gt=0)
    menu_item_id: int = Field(..., gt=0)
    quantity: int = Field(1, ge=1, le=100)
    has_modifiers: bool = False
    current_queue_size: int = Field(0, ge=0, le=100)

# Usage in endpoints
@app.post('/api/predictions/kitchen/prep-time')
async def predict_prep_time(request: PrepTimeRequest):
    """Predict prep time with validation."""
    # Request is automatically validated
    # ... rest of logic
```

## Secrets Management

### Environment Variables

```bash
# .env (never commit to git)
RMS_DB_URL=postgresql://user:password@host:5432/db
REDIS_URL=redis://host:6379/0
API_KEY_SECRET=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
```

### AWS Secrets Manager (Production)

```python
# src/utils/secrets.py
import boto3
import json

class SecretsManager:
    """Manage secrets from AWS Secrets Manager."""

    def __init__(self, region_name='us-east-1'):
        self.client = boto3.client('secretsmanager', region_name=region_name)

    def get_secret(self, secret_name: str) -> dict:
        """Get secret from AWS Secrets Manager."""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            return json.loads(response['SecretString'])
        except Exception as e:
            logger.error(f"Error retrieving secret: {e}")
            raise

# Usage
secrets_manager = SecretsManager()
db_credentials = secrets_manager.get_secret('ml-service/rms-db')
```

## Audit Logging

### Security Audit Log

```python
# src/utils/audit_log.py
import logging
from datetime import datetime

class AuditLogger:
    """Log security-relevant events."""

    def __init__(self):
        self.logger = logging.getLogger('security_audit')

    def log_authentication(
        self,
        api_key_hash: str,
        success: bool,
        ip_address: str
    ):
        """Log authentication attempt."""
        self.logger.info({
            'event': 'authentication',
            'api_key_hash': api_key_hash,
            'success': success,
            'ip_address': ip_address,
            'timestamp': datetime.now().isoformat()
        })

    def log_data_access(
        self,
        user: str,
        resource: str,
        action: str,
        restaurant_id: int
    ):
        """Log data access."""
        self.logger.info({
            'event': 'data_access',
            'user': user,
            'resource': resource,
            'action': action,
            'restaurant_id': restaurant_id,
            'timestamp': datetime.now().isoformat()
        })

    def log_model_access(
        self,
        user: str,
        model_type: str,
        restaurant_id: int
    ):
        """Log model access."""
        self.logger.info({
            'event': 'model_access',
            'user': user,
            'model_type': model_type,
            'restaurant_id': restaurant_id,
            'timestamp': datetime.now().isoformat()
        })
```

## Security Checklist

### Pre-Deployment

- [ ] All secrets stored securely (not in code)
- [ ] Database user has read-only access
- [ ] SSL/TLS enabled for all connections
- [ ] API authentication implemented
- [ ] Rate limiting configured
- [ ] Input validation on all endpoints
- [ ] CORS configured properly
- [ ] Security headers added
- [ ] Firewall rules configured
- [ ] Audit logging enabled

### Post-Deployment

- [ ] Monitor authentication failures
- [ ] Review audit logs regularly
- [ ] Update dependencies for security patches
- [ ] Rotate API keys periodically
- [ ] Review access logs for anomalies
- [ ] Test disaster recovery procedures
- [ ] Conduct security audits
- [ ] Update SSL certificates before expiry

---

**Next**: [Development Guide](./10-DEVELOPMENT.md)

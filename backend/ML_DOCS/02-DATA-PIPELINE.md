# Data Pipeline

## Overview

The data pipeline extracts, transforms, and prepares data from the RMS database for ML model training and predictions. It ensures data quality, handles missing values, and creates features optimized for machine learning.

## Pipeline Architecture

```
RMS PostgreSQL → Data Extractor → Data Validator → Data Processor → Feature Engineer → ML Models
                      ↓                ↓                 ↓                ↓
                   Raw Data      Validation Log    Clean Data      Feature Store
```

## Data Sources

### 1. Orders Data

**Tables**: `orders_order`, `orders_orderitem`

**Key Fields**:

```sql
-- orders_order
id, restaurant_id, table_id, waiter_id, customer_id,
service_type, order_number, order_display_token,
status, payment_status, subtotal, tax_total, grand_total,
discount_percentage, discount_amount, tip_amount,
created_at, updated_at, party_size

-- orders_orderitem
id, order_id, menu_item_id, quantity, unit_price,
subtotal, discount_percentage, discount_amount,
special_instructions, realized_recipe_cost
```

**Use Cases**:

- Demand forecasting (order volume, item popularity)
- Revenue prediction
- Customer behavior analysis
- Pricing optimization

**Extraction Query**:

```sql
SELECT
    o.id,
    o.restaurant_id,
    o.service_type,
    o.grand_total,
    o.created_at,
    DATE_TRUNC('hour', o.created_at) as order_hour,
    EXTRACT(DOW FROM o.created_at) as day_of_week,
    EXTRACT(HOUR FROM o.created_at) as hour_of_day,
    oi.menu_item_id,
    mi.name as item_name,
    mc.name as category_name,
    oi.quantity,
    oi.unit_price
FROM orders_order o
JOIN orders_orderitem oi ON o.id = oi.order_id
JOIN menus_menuitem mi ON oi.menu_item_id = mi.id
JOIN menus_menucategory mc ON mi.category_id = mc.id
WHERE o.restaurant_id = %s
  AND o.status IN ('completed', 'paid')
  AND o.created_at >= %s
  AND o.created_at < %s
ORDER BY o.created_at;
```

### 2. Kitchen Performance Data

**Tables**: `kitchen_orderitemstation`

**Key Fields**:

```sql
id, order_item_id, station_id, status,
assigned_at, started_at, completed_at,
assigned_to_id
```

**Use Cases**:

- Prep time estimation
- Bottleneck detection
- Staff productivity analysis
- Queue time prediction

**Extraction Query**:

```sql
SELECT
    ois.id,
    ois.station_id,
    ks.name as station_name,
    oi.menu_item_id,
    mi.name as item_name,
    oi.quantity,
    ois.assigned_at,
    ois.started_at,
    ois.completed_at,
    EXTRACT(EPOCH FROM (ois.completed_at - ois.assigned_at))/60 as total_time_minutes,
    EXTRACT(EPOCH FROM (ois.completed_at - ois.started_at))/60 as prep_time_minutes,
    EXTRACT(EPOCH FROM (ois.started_at - ois.assigned_at))/60 as queue_time_minutes,
    EXTRACT(DOW FROM ois.assigned_at) as day_of_week,
    EXTRACT(HOUR FROM ois.assigned_at) as hour_of_day
FROM kitchen_orderitemstation ois
JOIN kitchen_kitchenstation ks ON ois.station_id = ks.id
JOIN orders_orderitem oi ON ois.order_item_id = oi.id
JOIN menus_menuitem mi ON oi.menu_item_id = mi.id
WHERE ks.restaurant_id = %s
  AND ois.status = 'completed'
  AND ois.completed_at IS NOT NULL
  AND ois.assigned_at >= %s
ORDER BY ois.assigned_at;
```

### 3. Customer Data

**Tables**: `crm_customerprofile`, `crm_loyaltybalance`, `crm_loyaltytransaction`

**Key Fields**:

```sql
-- crm_customerprofile
id, restaurant_id, full_name, phone_number, email,
birth_date, created_at, consent_marketing

-- crm_loyaltybalance
customer_id, current_points, lifetime_points,
current_tier, tier_since

-- crm_loyaltytransaction
customer_id, transaction_type, points, order_id,
created_at
```

**Use Cases**:

- Churn prediction
- Lifetime value estimation
- Loyalty tier progression
- Personalized recommendations

**Extraction Query**:

```sql
SELECT
    cp.id as customer_id,
    cp.restaurant_id,
    cp.created_at as customer_since,
    EXTRACT(EPOCH FROM (NOW() - cp.created_at))/86400 as days_since_signup,
    lb.current_points,
    lb.lifetime_points,
    lb.current_tier,
    COUNT(DISTINCT o.id) as total_orders,
    SUM(o.grand_total) as total_spent,
    AVG(o.grand_total) as avg_order_value,
    MAX(o.created_at) as last_order_date,
    EXTRACT(EPOCH FROM (NOW() - MAX(o.created_at)))/86400 as days_since_last_order,
    COUNT(DISTINCT DATE(o.created_at)) as unique_order_days
FROM crm_customerprofile cp
LEFT JOIN crm_loyaltybalance lb ON cp.id = lb.customer_id
LEFT JOIN orders_order o ON cp.id = o.customer_id AND o.status IN ('completed', 'paid')
WHERE cp.restaurant_id = %s
GROUP BY cp.id, lb.current_points, lb.lifetime_points, lb.current_tier;
```

### 4. Inventory Data

**Tables**: `inventory_inventoryitem`, `inventory_batch`, `inventory_stockmovement`

**Key Fields**:

```sql
-- inventory_inventoryitem
id, restaurant_id, name, sku, category_id,
min_level, reorder_level, auto_reorder_enabled

-- inventory_batch
id, item_id, qty_base, remaining_base,
unit_cost_per_base, received_at, expiry_date

-- inventory_stockmovement
id, item_id, movement_type, qty_base,
unit_cost_per_base, created_at, reason
```

**Use Cases**:

- Stock level optimization
- Reorder point prediction
- Expiry prediction
- Waste reduction

**Extraction Query**:

```sql
SELECT
    ii.id as item_id,
    ii.restaurant_id,
    ii.name as item_name,
    ic.name as category_name,
    ii.min_level,
    ii.reorder_level,
    SUM(b.remaining_base) as current_stock,
    COUNT(b.id) as batch_count,
    MIN(b.expiry_date) as earliest_expiry,
    AVG(b.unit_cost_per_base) as avg_unit_cost,
    -- Consumption rate (last 30 days)
    (SELECT SUM(ABS(sm.qty_base))
     FROM inventory_stockmovement sm
     WHERE sm.item_id = ii.id
       AND sm.movement_type = 'recipe_deduct'
       AND sm.created_at >= NOW() - INTERVAL '30 days'
    ) as consumption_last_30_days,
    -- Days until stockout (if consumption continues)
    CASE
        WHEN (SELECT SUM(ABS(sm.qty_base))
              FROM inventory_stockmovement sm
              WHERE sm.item_id = ii.id
                AND sm.movement_type = 'recipe_deduct'
                AND sm.created_at >= NOW() - INTERVAL '30 days') > 0
        THEN (SUM(b.remaining_base) /
              (SELECT SUM(ABS(sm.qty_base))/30
               FROM inventory_stockmovement sm
               WHERE sm.item_id = ii.id
                 AND sm.movement_type = 'recipe_deduct'
                 AND sm.created_at >= NOW() - INTERVAL '30 days'))
        ELSE NULL
    END as estimated_days_until_stockout
FROM inventory_inventoryitem ii
LEFT JOIN inventory_category ic ON ii.category_id = ic.id
LEFT JOIN inventory_batch b ON ii.id = b.item_id AND b.remaining_base > 0
WHERE ii.restaurant_id = %s
  AND ii.is_active = TRUE
GROUP BY ii.id, ic.name;
```

### 5. Payment Data

**Tables**: `payments_payment`

**Key Fields**:

```sql
id, order_id, restaurant_id, payment_method,
amount, tip_amount, status, created_at, completed_at
```

**Use Cases**:

- Payment method preference analysis
- Tip prediction
- Payment timing patterns
- Fraud detection

## Data Extraction Module

### Database Connection

**File**: `src/pipelines/data_extractor.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import pandas as pd
from typing import Optional, Dict, Any
import logging

class RMSDataExtractor:
    """Extract data from RMS PostgreSQL database (read-only)."""

    def __init__(self, db_url: str):
        """
        Initialize database connection.

        Args:
            db_url: PostgreSQL connection string
                   postgresql://user:pass@host:port/dbname
        """
        self.engine = create_engine(
            db_url,
            poolclass=NullPool,  # No connection pooling for read-only
            connect_args={
                'options': '-c default_transaction_read_only=on'
            }
        )
        self.logger = logging.getLogger(__name__)

    def extract_orders(
        self,
        restaurant_id: int,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """Extract order data for demand forecasting."""
        query = """
        SELECT
            o.id,
            o.restaurant_id,
            o.service_type,
            o.grand_total,
            o.created_at,
            DATE_TRUNC('hour', o.created_at) as order_hour,
            EXTRACT(DOW FROM o.created_at) as day_of_week,
            EXTRACT(HOUR FROM o.created_at) as hour_of_day,
            oi.menu_item_id,
            mi.name as item_name,
            mc.name as category_name,
            oi.quantity,
            oi.unit_price
        FROM orders_order o
        JOIN orders_orderitem oi ON o.id = oi.order_id
        JOIN menus_menuitem mi ON oi.menu_item_id = mi.id
        JOIN menus_menucategory mc ON mi.category_id = mc.id
        WHERE o.restaurant_id = %(restaurant_id)s
          AND o.status IN ('completed', 'paid')
          AND o.created_at >= %(start_date)s
          AND o.created_at < %(end_date)s
        ORDER BY o.created_at;
        """

        try:
            df = pd.read_sql(
                query,
                self.engine,
                params={
                    'restaurant_id': restaurant_id,
                    'start_date': start_date,
                    'end_date': end_date
                }
            )
            self.logger.info(f"Extracted {len(df)} order records")
            return df
        except Exception as e:
            self.logger.error(f"Error extracting orders: {e}")
            raise

    def extract_kitchen_performance(
        self,
        restaurant_id: int,
        start_date: str,
        days: int = 30
    ) -> pd.DataFrame:
        """Extract kitchen timing data."""
        # Implementation similar to above
        pass

    def extract_customer_data(
        self,
        restaurant_id: int
    ) -> pd.DataFrame:
        """Extract customer profiles and behavior."""
        # Implementation similar to above
        pass

    def extract_inventory_data(
        self,
        restaurant_id: int
    ) -> pd.DataFrame:
        """Extract inventory levels and consumption."""
        # Implementation similar to above
        pass
```

## Data Processing Module

### Data Cleaning

**File**: `src/pipelines/data_processor.py`

```python
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

class DataProcessor:
    """Clean and validate extracted data."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_orders(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate order data.

        Steps:
        1. Handle missing values
        2. Remove outliers
        3. Validate data types
        4. Create derived fields
        """
        # Make a copy
        df = df.copy()

        # Convert timestamps
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['order_hour'] = pd.to_datetime(df['order_hour'])

        # Handle missing values
        df['service_type'] = df['service_type'].fillna('DINE_IN')
        df['category_name'] = df['category_name'].fillna('Uncategorized')

        # Remove invalid records
        df = df[df['grand_total'] > 0]
        df = df[df['quantity'] > 0]

        # Remove outliers (orders > 3 std dev from mean)
        mean_total = df['grand_total'].mean()
        std_total = df['grand_total'].std()
        df = df[
            (df['grand_total'] >= mean_total - 3*std_total) &
            (df['grand_total'] <= mean_total + 3*std_total)
        ]

        # Create derived fields
        df['is_weekend'] = df['day_of_week'].isin([5, 6])  # Sat, Sun
        df['is_peak_hour'] = df['hour_of_day'].isin([12, 13, 18, 19, 20])
        df['order_date'] = df['created_at'].dt.date

        self.logger.info(f"Processed {len(df)} order records")
        return df

    def process_kitchen_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean kitchen performance data."""
        df = df.copy()

        # Convert timestamps
        df['assigned_at'] = pd.to_datetime(df['assigned_at'])
        df['started_at'] = pd.to_datetime(df['started_at'])
        df['completed_at'] = pd.to_datetime(df['completed_at'])

        # Remove records with missing timing
        df = df.dropna(subset=['assigned_at', 'completed_at'])

        # Remove negative or zero times (data errors)
        df = df[df['total_time_minutes'] > 0]
        df = df[df['prep_time_minutes'] > 0]

        # Remove extreme outliers (> 2 hours prep time)
        df = df[df['total_time_minutes'] <= 120]

        # Handle queue time (can be 0 if started immediately)
        df['queue_time_minutes'] = df['queue_time_minutes'].fillna(0)
        df['queue_time_minutes'] = df['queue_time_minutes'].clip(lower=0)

        return df

    def process_customer_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean customer data."""
        df = df.copy()

        # Convert timestamps
        df['customer_since'] = pd.to_datetime(df['customer_since'])
        df['last_order_date'] = pd.to_datetime(df['last_order_date'])

        # Handle missing values
        df['total_orders'] = df['total_orders'].fillna(0)
        df['total_spent'] = df['total_spent'].fillna(0)
        df['current_points'] = df['current_points'].fillna(0)
        df['current_tier'] = df['current_tier'].fillna('bronze')

        # Remove customers with no orders
        df = df[df['total_orders'] > 0]

        # Calculate recency, frequency, monetary (RFM)
        df['recency_days'] = df['days_since_last_order']
        df['frequency'] = df['total_orders']
        df['monetary'] = df['total_spent']

        return df

    def process_inventory_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean inventory data."""
        df = df.copy()

        # Handle missing values
        df['current_stock'] = df['current_stock'].fillna(0)
        df['consumption_last_30_days'] = df['consumption_last_30_days'].fillna(0)
        df['batch_count'] = df['batch_count'].fillna(0)

        # Calculate consumption rate
        df['daily_consumption_rate'] = df['consumption_last_30_days'] / 30

        # Calculate stock status
        df['stock_status'] = df.apply(
            lambda row: 'low' if row['current_stock'] <= row['min_level']
            else 'medium' if row['current_stock'] <= row['reorder_level']
            else 'high',
            axis=1
        )

        return df
```

## Feature Engineering

### Feature Creation

**File**: `src/pipelines/feature_engineering.py`

```python
import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta

class FeatureEngineer:
    """Create ML features from processed data."""

    def create_demand_features(
        self,
        df: pd.DataFrame,
        target_date: datetime
    ) -> pd.DataFrame:
        """
        Create features for demand forecasting.

        Features:
        - Time-based: hour, day_of_week, month, is_weekend, is_holiday
        - Lag features: orders 1/7/30 days ago
        - Rolling averages: 7-day, 30-day moving averages
        - Trend: linear trend over time
        - Seasonality: cyclical encoding of time features
        """
        features = pd.DataFrame()

        # Time-based features
        features['hour'] = target_date.hour
        features['day_of_week'] = target_date.weekday()
        features['day_of_month'] = target_date.day
        features['month'] = target_date.month
        features['is_weekend'] = int(target_date.weekday() >= 5)
        features['is_peak_hour'] = int(target_date.hour in [12, 13, 18, 19, 20])

        # Cyclical encoding (for periodicity)
        features['hour_sin'] = np.sin(2 * np.pi * target_date.hour / 24)
        features['hour_cos'] = np.cos(2 * np.pi * target_date.hour / 24)
        features['day_sin'] = np.sin(2 * np.pi * target_date.weekday() / 7)
        features['day_cos'] = np.cos(2 * np.pi * target_date.weekday() / 7)

        # Lag features (historical demand)
        features['orders_1d_ago'] = self._get_orders_at_time(
            df, target_date - timedelta(days=1)
        )
        features['orders_7d_ago'] = self._get_orders_at_time(
            df, target_date - timedelta(days=7)
        )
        features['orders_30d_ago'] = self._get_orders_at_time(
            df, target_date - timedelta(days=30)
        )

        # Rolling averages
        features['orders_7d_avg'] = self._get_rolling_avg(
            df, target_date, days=7
        )
        features['orders_30d_avg'] = self._get_rolling_avg(
            df, target_date, days=30
        )

        # Trend (days since first order)
        first_order_date = df['created_at'].min()
        features['days_since_start'] = (target_date - first_order_date).days

        return features

    def create_kitchen_features(
        self,
        df: pd.DataFrame,
        station_id: int,
        menu_item_id: int
    ) -> Dict:
        """
        Create features for kitchen performance prediction.

        Features:
        - Item characteristics: complexity, modifiers
        - Station load: current queue size
        - Historical performance: avg prep time for item/station
        - Time context: hour, day_of_week
        - Staff: assigned staff experience level
        """
        # Filter for specific station and item
        item_station_df = df[
            (df['station_id'] == station_id) &
            (df['menu_item_id'] == menu_item_id)
        ]

        features = {}

        # Historical averages
        if len(item_station_df) > 0:
            features['avg_prep_time'] = item_station_df['prep_time_minutes'].mean()
            features['std_prep_time'] = item_station_df['prep_time_minutes'].std()
            features['min_prep_time'] = item_station_df['prep_time_minutes'].min()
            features['max_prep_time'] = item_station_df['prep_time_minutes'].max()
        else:
            # Use station averages if no item history
            station_df = df[df['station_id'] == station_id]
            features['avg_prep_time'] = station_df['prep_time_minutes'].mean()
            features['std_prep_time'] = station_df['prep_time_minutes'].std()
            features['min_prep_time'] = station_df['prep_time_minutes'].min()
            features['max_prep_time'] = station_df['prep_time_minutes'].max()

        # Item complexity (based on historical variance)
        features['item_complexity'] = features['std_prep_time'] / features['avg_prep_time'] if features['avg_prep_time'] > 0 else 0

        return features

    def create_customer_features(
        self,
        df: pd.DataFrame,
        customer_id: int
    ) -> Dict:
        """
        Create features for customer analytics.

        Features:
        - RFM: Recency, Frequency, Monetary
        - Loyalty: current tier, points, lifetime value
        - Behavior: avg order value, order frequency
        - Engagement: days since signup, total orders
        """
        customer = df[df['customer_id'] == customer_id].iloc[0]

        features = {
            # RFM
            'recency_days': customer['days_since_last_order'],
            'frequency': customer['total_orders'],
            'monetary': customer['total_spent'],

            # Loyalty
            'current_points': customer['current_points'],
            'lifetime_points': customer['lifetime_points'],
            'current_tier': customer['current_tier'],

            # Behavior
            'avg_order_value': customer['avg_order_value'],
            'days_since_signup': customer['days_since_signup'],
            'order_frequency': customer['total_orders'] / max(customer['days_since_signup'], 1),

            # Engagement
            'unique_order_days': customer['unique_order_days'],
            'orders_per_active_day': customer['total_orders'] / max(customer['unique_order_days'], 1),
        }

        return features

    def _get_orders_at_time(
        self,
        df: pd.DataFrame,
        target_time: datetime
    ) -> int:
        """Get order count at specific time."""
        hour_df = df[
            (df['created_at'] >= target_time) &
            (df['created_at'] < target_time + timedelta(hours=1))
        ]
        return len(hour_df)

    def _get_rolling_avg(
        self,
        df: pd.DataFrame,
        target_time: datetime,
        days: int
    ) -> float:
        """Calculate rolling average of orders."""
        start_time = target_time - timedelta(days=days)
        period_df = df[
            (df['created_at'] >= start_time) &
            (df['created_at'] < target_time)
        ]

        # Group by hour and calculate average
        hourly_counts = period_df.groupby(
            period_df['created_at'].dt.floor('H')
        ).size()

        return hourly_counts.mean() if len(hourly_counts) > 0 else 0
```

## Data Validation

### Validation Rules

```python
class DataValidator:
    """Validate data quality."""

    def validate_orders(self, df: pd.DataFrame) -> Dict:
        """Validate order data quality."""
        issues = []

        # Check for required columns
        required_cols = ['id', 'restaurant_id', 'created_at', 'grand_total']
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            issues.append(f"Missing columns: {missing_cols}")

        # Check for null values in critical fields
        null_counts = df[required_cols].isnull().sum()
        if null_counts.any():
            issues.append(f"Null values found: {null_counts[null_counts > 0].to_dict()}")

        # Check for negative values
        if (df['grand_total'] < 0).any():
            issues.append("Negative grand_total values found")

        # Check for future dates
        if (df['created_at'] > pd.Timestamp.now()).any():
            issues.append("Future dates found in created_at")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'record_count': len(df)
        }
```

## Caching Strategy

### Feature Cache

```python
import redis
import json
import hashlib

class FeatureCache:
    """Cache processed features."""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.ttl = 3600 * 6  # 6 hours

    def get_features(self, key: str) -> Optional[Dict]:
        """Get cached features."""
        cached = self.redis.get(f"ml:features:{key}")
        if cached:
            return json.loads(cached)
        return None

    def set_features(self, key: str, features: Dict):
        """Cache features."""
        self.redis.setex(
            f"ml:features:{key}",
            self.ttl,
            json.dumps(features)
        )

    def generate_key(self, **kwargs) -> str:
        """Generate cache key from parameters."""
        key_str = json.dumps(kwargs, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
```

## Performance Optimization

### Query Optimization

- Use indexes on timestamp columns
- Limit date ranges to necessary periods
- Use aggregations in SQL vs Python
- Batch queries when possible

### Memory Management

- Process data in chunks for large datasets
- Use generators for streaming data
- Clear DataFrames after processing
- Use appropriate data types (int32 vs int64)

### Parallel Processing

- Use multiprocessing for independent extractions
- Parallel feature engineering for multiple entities
- Async database queries

---

**Next**: [ML Models](./03-ML-MODELS.md)

# ML Models

## Overview

This document describes the machine learning models used in the RMS ML service, including algorithms, training procedures, evaluation metrics, and deployment strategies.

## Model Catalog

### 1. Demand Forecasting Model

**Purpose**: Predict order volume and item demand

**Algorithm**: XGBoost Regressor + Prophet (ensemble)

**Input Features**:

- Time features: hour, day_of_week, month, is_weekend, is_holiday
- Cyclical encodings: hour_sin, hour_cos, day_sin, day_cos
- Lag features: orders 1/7/30 days ago
- Rolling averages: 7-day, 30-day moving averages
- Trend: days_since_start
- External: weather, events (future)

**Target Variable**:

- Order count per hour
- Item quantity per hour
- Revenue per hour

**Model Architecture**:

```python
from xgboost import XGBRegressor
from prophet import Prophet
import numpy as np

class DemandForecastModel:
    def __init__(self):
        # XGBoost for short-term predictions (hours/days)
        self.xgb_model = XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )

        # Prophet for long-term trends (weeks/months)
        self.prophet_model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=True,
            changepoint_prior_scale=0.05
        )

        self.ensemble_weight = 0.7  # 70% XGBoost, 30% Prophet

    def train(self, X_train, y_train, dates):
        # Train XGBoost
        self.xgb_model.fit(X_train, y_train)

        # Train Prophet
        prophet_df = pd.DataFrame({
            'ds': dates,
            'y': y_train
        })
        self.prophet_model.fit(prophet_df)

    def predict(self, X_test, dates):
        # XGBoost predictions
        xgb_pred = self.xgb_model.predict(X_test)

        # Prophet predictions
        prophet_df = pd.DataFrame({'ds': dates})
        prophet_pred = self.prophet_model.predict(prophet_df)['yhat'].values

        # Ensemble
        final_pred = (
            self.ensemble_weight * xgb_pred +
            (1 - self.ensemble_weight) * prophet_pred
        )

        return np.maximum(final_pred, 0)  # No negative predictions
```

**Training Data Requirements**:

- Minimum: 3 months of historical data
- Recommended: 6-12 months
- Update frequency: Daily

**Evaluation Metrics**:

- MAE (Mean Absolute Error): Target < 5 orders/hour
- RMSE (Root Mean Squared Error): Target < 8 orders/hour
- MAPE (Mean Absolute Percentage Error): Target < 15%
- R² Score: Target > 0.85

**Model Variants**:

- `demand_hourly`: Hourly predictions (next 24-48 hours)
- `demand_daily`: Daily predictions (next 7-30 days)
- `demand_item`: Item-level demand (top 50 items)
- `demand_category`: Category-level demand

---

### 2. Kitchen Performance Model

**Purpose**: Predict preparation time for orders

**Algorithm**: LightGBM Regressor

**Input Features**:

- Item features: item_id, category, complexity_score
- Station features: station_id, current_queue_size
- Historical features: avg_prep_time, std_prep_time
- Time features: hour_of_day, day_of_week, is_peak_hour
- Order features: quantity, has_modifiers, special_instructions
- Staff features: assigned_staff_experience (future)

**Target Variable**: Preparation time in minutes

**Model Architecture**:

```python
from lightgbm import LGBMRegressor

class KitchenPerformanceModel:
    def __init__(self):
        self.model = LGBMRegressor(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.05,
            num_leaves=31,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )

        self.scaler = StandardScaler()

    def train(self, X_train, y_train):
        X_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_scaled, y_train)

    def predict(self, X_test):
        X_scaled = self.scaler.transform(X_test)
        predictions = self.model.predict(X_scaled)

        # Add confidence intervals
        std_pred = np.std(predictions)
        lower_bound = predictions - 1.96 * std_pred
        upper_bound = predictions + 1.96 * std_pred

        return {
            'predicted_time': predictions,
            'lower_bound': np.maximum(lower_bound, 0),
            'upper_bound': upper_bound
        }
```

**Training Data Requirements**:

- Minimum: 1000 completed orders per station
- Recommended: 5000+ completed orders
- Update frequency: Daily

**Evaluation Metrics**:

- MAE: Target < 2 minutes
- RMSE: Target < 3 minutes
- Within 5 minutes accuracy: Target > 80%
- R² Score: Target > 0.75

---

### 3. Customer Churn Prediction Model

**Purpose**: Predict likelihood of customer churn

**Algorithm**: XGBoost Classifier

**Input Features**:

- RFM: recency_days, frequency, monetary
- Loyalty: current_points, lifetime_points, current_tier
- Behavior: avg_order_value, order_frequency, orders_per_active_day
- Engagement: days_since_signup, unique_order_days
- Trend: order_frequency_trend (increasing/decreasing)

**Target Variable**: Churned (1) or Active (0)

- Churned defined as: No order in last 60 days (configurable)

**Model Architecture**:

```python
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler

class CustomerChurnModel:
    def __init__(self):
        self.model = XGBClassifier(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.1,
            scale_pos_weight=3,  # Handle class imbalance
            random_state=42
        )

        self.scaler = StandardScaler()
        self.threshold = 0.5  # Probability threshold

    def train(self, X_train, y_train):
        X_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_scaled, y_train)

    def predict_proba(self, X_test):
        X_scaled = self.scaler.transform(X_test)
        return self.model.predict_proba(X_scaled)[:, 1]

    def predict(self, X_test):
        proba = self.predict_proba(X_test)
        return (proba >= self.threshold).astype(int)

    def get_risk_segments(self, X_test):
        """Segment customers by churn risk."""
        proba = self.predict_proba(X_test)

        segments = []
        for p in proba:
            if p < 0.3:
                segments.append('low_risk')
            elif p < 0.6:
                segments.append('medium_risk')
            else:
                segments.append('high_risk')

        return segments
```

**Training Data Requirements**:

- Minimum: 500 customers with at least 2 orders
- Recommended: 2000+ customers
- Update frequency: Weekly

**Evaluation Metrics**:

- Precision: Target > 0.70 (avoid false alarms)
- Recall: Target > 0.65 (catch churners)
- F1 Score: Target > 0.67
- AUC-ROC: Target > 0.80

---

### 4. Customer Lifetime Value (LTV) Model

**Purpose**: Predict customer lifetime value

**Algorithm**: Random Forest Regressor

**Input Features**:

- Same as churn model
- Additional: first_order_value, days_to_second_order

**Target Variable**: Total revenue in next 12 months

**Model Architecture**:

```python
from sklearn.ensemble import RandomForestRegressor

class CustomerLTVModel:
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42
        )

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def predict(self, X_test):
        predictions = self.model.predict(X_test)
        return np.maximum(predictions, 0)

    def get_ltv_segments(self, X_test):
        """Segment customers by predicted LTV."""
        ltv = self.predict(X_test)

        # Define segments based on percentiles
        p33 = np.percentile(ltv, 33)
        p67 = np.percentile(ltv, 67)

        segments = []
        for value in ltv:
            if value < p33:
                segments.append('low_value')
            elif value < p67:
                segments.append('medium_value')
            else:
                segments.append('high_value')

        return segments
```

**Training Data Requirements**:

- Minimum: 500 customers with 6+ months history
- Recommended: 2000+ customers
- Update frequency: Weekly

**Evaluation Metrics**:

- MAE: Target < 20% of average LTV
- RMSE: Target < 30% of average LTV
- R² Score: Target > 0.70

---

### 5. Inventory Optimization Model

**Purpose**: Predict optimal stock levels and reorder points

**Algorithm**: Time Series + Optimization

**Input Features**:

- Historical consumption: daily_consumption_rate
- Seasonality: day_of_week, month, is_holiday
- Lead time: supplier_lead_time_days
- Demand forecast: predicted_order_volume
- Cost factors: holding_cost, stockout_cost

**Target Variable**:

- Optimal reorder point
- Optimal order quantity

**Model Architecture**:

```python
from scipy.optimize import minimize
import numpy as np

class InventoryOptimizationModel:
    def __init__(self):
        self.demand_model = None  # Use demand forecast model
        self.holding_cost_per_unit_per_day = 0.01
        self.stockout_cost_per_unit = 10.0
        self.service_level = 0.95  # 95% service level

    def predict_reorder_point(
        self,
        item_id: int,
        lead_time_days: int,
        demand_forecast: np.ndarray
    ):
        """Calculate optimal reorder point."""
        # Average demand during lead time
        avg_demand = np.mean(demand_forecast[:lead_time_days])

        # Standard deviation of demand
        std_demand = np.std(demand_forecast[:lead_time_days])

        # Safety stock (z-score for service level)
        z_score = 1.65  # 95% service level
        safety_stock = z_score * std_demand * np.sqrt(lead_time_days)

        # Reorder point
        reorder_point = avg_demand * lead_time_days + safety_stock

        return {
            'reorder_point': max(reorder_point, 0),
            'safety_stock': safety_stock,
            'avg_demand_during_lead_time': avg_demand * lead_time_days
        }

    def predict_order_quantity(
        self,
        item_id: int,
        annual_demand: float,
        order_cost: float,
        holding_cost: float
    ):
        """Calculate Economic Order Quantity (EOQ)."""
        # EOQ formula
        eoq = np.sqrt((2 * annual_demand * order_cost) / holding_cost)

        return {
            'optimal_order_quantity': eoq,
            'orders_per_year': annual_demand / eoq,
            'total_cost': (annual_demand / eoq) * order_cost + (eoq / 2) * holding_cost
        }
```

**Training Data Requirements**:

- Minimum: 3 months of consumption data
- Recommended: 6-12 months
- Update frequency: Weekly

**Evaluation Metrics**:

- Stockout rate: Target < 5%
- Excess inventory: Target < 15%
- Inventory turnover: Target improvement > 10%

---

## Model Training Pipeline

### Training Workflow

```python
# src/training/train_pipeline.py

class ModelTrainingPipeline:
    def __init__(self, model_type: str):
        self.model_type = model_type
        self.data_extractor = RMSDataExtractor()
        self.data_processor = DataProcessor()
        self.feature_engineer = FeatureEngineer()

    def run(self, restaurant_id: int):
        """Execute full training pipeline."""

        # 1. Extract data
        print(f"Extracting data for {self.model_type}...")
        raw_data = self.data_extractor.extract(
            model_type=self.model_type,
            restaurant_id=restaurant_id
        )

        # 2. Process data
        print("Processing data...")
        clean_data = self.data_processor.process(raw_data)

        # 3. Validate data
        validation = self.data_processor.validate(clean_data)
        if not validation['valid']:
            raise ValueError(f"Data validation failed: {validation['issues']}")

        # 4. Engineer features
        print("Engineering features...")
        X, y = self.feature_engineer.create_features(
            clean_data,
            model_type=self.model_type
        )

        # 5. Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # 6. Train model
        print("Training model...")
        model = self._get_model_instance()
        model.train(X_train, y_train)

        # 7. Evaluate model
        print("Evaluating model...")
        metrics = self._evaluate_model(model, X_test, y_test)

        # 8. Save model
        print("Saving model...")
        self._save_model(model, metrics, restaurant_id)

        return metrics

    def _get_model_instance(self):
        """Get model instance based on type."""
        models = {
            'demand': DemandForecastModel,
            'kitchen': KitchenPerformanceModel,
            'churn': CustomerChurnModel,
            'ltv': CustomerLTVModel,
            'inventory': InventoryOptimizationModel
        }
        return models[self.model_type]()

    def _evaluate_model(self, model, X_test, y_test):
        """Evaluate model performance."""
        predictions = model.predict(X_test)

        if self.model_type in ['demand', 'kitchen', 'ltv']:
            # Regression metrics
            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

            metrics = {
                'mae': mean_absolute_error(y_test, predictions),
                'rmse': np.sqrt(mean_squared_error(y_test, predictions)),
                'r2': r2_score(y_test, predictions),
                'mape': np.mean(np.abs((y_test - predictions) / y_test)) * 100
            }
        else:
            # Classification metrics
            from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score

            metrics = {
                'precision': precision_score(y_test, predictions),
                'recall': recall_score(y_test, predictions),
                'f1': f1_score(y_test, predictions),
                'auc_roc': roc_auc_score(y_test, model.predict_proba(X_test))
            }

        return metrics

    def _save_model(self, model, metrics, restaurant_id):
        """Save model with versioning."""
        import joblib
        from datetime import datetime

        version = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_dir = f"models/{self.model_type}/restaurant_{restaurant_id}/{version}"
        os.makedirs(model_dir, exist_ok=True)

        # Save model
        joblib.dump(model, f"{model_dir}/model.joblib")

        # Save metadata
        metadata = {
            'model_type': self.model_type,
            'restaurant_id': restaurant_id,
            'version': version,
            'trained_at': datetime.now().isoformat(),
            'metrics': metrics,
            'feature_names': model.feature_names if hasattr(model, 'feature_names') else []
        }

        with open(f"{model_dir}/metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)

        # Update 'latest' symlink
        latest_link = f"models/{self.model_type}/restaurant_{restaurant_id}/latest"
        if os.path.exists(latest_link):
            os.remove(latest_link)
        os.symlink(model_dir, latest_link)
```

### Hyperparameter Tuning

```python
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

class HyperparameterTuner:
    def __init__(self, model_type: str):
        self.model_type = model_type

    def tune(self, X_train, y_train):
        """Tune hyperparameters using grid search."""

        if self.model_type == 'demand':
            param_grid = {
                'n_estimators': [100, 200, 300],
                'max_depth': [4, 6, 8],
                'learning_rate': [0.05, 0.1, 0.2],
                'subsample': [0.7, 0.8, 0.9]
            }
            model = XGBRegressor()

        elif self.model_type == 'kitchen':
            param_grid = {
                'n_estimators': [150, 200, 250],
                'max_depth': [6, 8, 10],
                'learning_rate': [0.03, 0.05, 0.1],
                'num_leaves': [31, 63, 127]
            }
            model = LGBMRegressor()

        # Grid search
        grid_search = GridSearchCV(
            model,
            param_grid,
            cv=5,
            scoring='neg_mean_absolute_error',
            n_jobs=-1
        )

        grid_search.fit(X_train, y_train)

        return grid_search.best_params_, grid_search.best_score_
```

## Model Versioning

### Version Control Strategy

```
models/
├── demand_forecasting/
│   ├── restaurant_1/
│   │   ├── 20260219_100000/
│   │   │   ├── model.joblib
│   │   │   ├── scaler.joblib
│   │   │   ├── metadata.json
│   │   │   └── metrics.json
│   │   ├── 20260218_100000/
│   │   └── latest -> 20260219_100000/
│   └── restaurant_2/
│       └── ...
└── kitchen_performance/
    └── ...
```

### Model Registry

```python
class ModelRegistry:
    """Track and manage model versions."""

    def __init__(self, redis_client):
        self.redis = redis_client

    def register_model(
        self,
        model_type: str,
        restaurant_id: int,
        version: str,
        metrics: Dict
    ):
        """Register a new model version."""
        key = f"ml:registry:{model_type}:restaurant_{restaurant_id}"

        model_info = {
            'version': version,
            'registered_at': datetime.now().isoformat(),
            'metrics': metrics,
            'status': 'active'
        }

        self.redis.hset(key, version, json.dumps(model_info))

    def get_latest_version(
        self,
        model_type: str,
        restaurant_id: int
    ) -> str:
        """Get latest model version."""
        key = f"ml:registry:{model_type}:restaurant_{restaurant_id}"
        versions = self.redis.hgetall(key)

        if not versions:
            return None

        # Get version with latest timestamp
        latest = max(
            versions.items(),
            key=lambda x: json.loads(x[1])['registered_at']
        )

        return latest[0]
```

## Model Monitoring

### Performance Tracking

```python
class ModelMonitor:
    """Monitor model performance in production."""

    def __init__(self):
        self.metrics_store = {}

    def log_prediction(
        self,
        model_type: str,
        restaurant_id: int,
        prediction: float,
        actual: float = None,
        features: Dict = None
    ):
        """Log prediction for monitoring."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'model_type': model_type,
            'restaurant_id': restaurant_id,
            'prediction': prediction,
            'actual': actual,
            'features': features
        }

        # Store in database or time-series DB
        self._store_log(log_entry)

    def detect_drift(
        self,
        model_type: str,
        restaurant_id: int,
        window_days: int = 7
    ) -> Dict:
        """Detect model drift."""
        # Get recent predictions and actuals
        recent_data = self._get_recent_data(
            model_type,
            restaurant_id,
            window_days
        )

        if len(recent_data) < 100:
            return {'drift_detected': False, 'reason': 'insufficient_data'}

        # Calculate current performance
        predictions = [d['prediction'] for d in recent_data]
        actuals = [d['actual'] for d in recent_data if d['actual'] is not None]

        if len(actuals) < 50:
            return {'drift_detected': False, 'reason': 'insufficient_actuals'}

        current_mae = mean_absolute_error(actuals, predictions[:len(actuals)])

        # Compare with training performance
        training_mae = self._get_training_mae(model_type, restaurant_id)

        # Drift if current MAE is 20% worse than training
        drift_threshold = training_mae * 1.2
        drift_detected = current_mae > drift_threshold

        return {
            'drift_detected': drift_detected,
            'current_mae': current_mae,
            'training_mae': training_mae,
            'threshold': drift_threshold,
            'degradation_pct': ((current_mae - training_mae) / training_mae) * 100
        }
```

---

**Next**: [API Reference](./04-API-REFERENCE.md)

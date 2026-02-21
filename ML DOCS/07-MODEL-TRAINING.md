# Model Training Guide

## Overview

This guide covers the complete process of training, evaluating, and deploying ML models for the restaurant management system.

## Training Workflow

```
Data Extraction → Data Processing → Feature Engineering → Model Training →
Evaluation → Validation → Deployment → Monitoring
```

## Training Scripts

### Demand Forecasting Model

**File**: `scripts/train_demand_model.py`

```python
#!/usr/bin/env python
"""Train demand forecasting model."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipelines.data_extractor import RMSDataExtractor
from src.pipelines.data_processor import DataProcessor
from src.pipelines.feature_engineering import FeatureEngineer
from src.training.demand_trainer import DemandForecastTrainer
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main training function."""
    # Configuration
    restaurant_id = int(os.getenv('RESTAURANT_ID', 1))
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)  # 6 months of data

    logger.info(f"Training demand model for restaurant {restaurant_id}")
    logger.info(f"Date range: {start_date} to {end_date}")

    # Step 1: Extract data
    logger.info("Step 1: Extracting data...")
    extractor = RMSDataExtractor(os.getenv('RMS_DB_URL'))
    raw_data = extractor.extract_orders(
        restaurant_id=restaurant_id,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )
    logger.info(f"Extracted {len(raw_data)} records")

    # Step 2: Process data
    logger.info("Step 2: Processing data...")
    processor = DataProcessor()
    clean_data = processor.process_orders(raw_data)
    logger.info(f"Processed {len(clean_data)} records")

    # Step 3: Validate data
    logger.info("Step 3: Validating data...")
    validation = processor.validate_orders(clean_data)
    if not validation['valid']:
        logger.error(f"Data validation failed: {validation['issues']}")
        sys.exit(1)
    logger.info("Data validation passed")

    # Step 4: Engineer features
    logger.info("Step 4: Engineering features...")
    engineer = FeatureEngineer()
    X, y, dates = engineer.create_demand_features(clean_data)
    logger.info(f"Created features: {X.shape}")

    # Step 5: Train model
    logger.info("Step 5: Training model...")
    trainer = DemandForecastTrainer()
    model, metrics = trainer.train(X, y, dates)
    logger.info(f"Training complete. Metrics: {metrics}")

    # Step 6: Save model
    logger.info("Step 6: Saving model...")
    trainer.save_model(model, metrics, restaurant_id)
    logger.info("Model saved successfully")

    # Step 7: Validate model
    logger.info("Step 7: Validating model...")
    if metrics['mae'] > 10:
        logger.warning(f"Model MAE ({metrics['mae']}) exceeds threshold (10)")
    if metrics['r2'] < 0.7:
        logger.warning(f"Model R² ({metrics['r2']}) below threshold (0.7)")

    logger.info("Training complete!")
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

### Kitchen Performance Model

**File**: `scripts/train_kitchen_model.py`

```python
#!/usr/bin/env python
"""Train kitchen performance model."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipelines.data_extractor import RMSDataExtractor
from src.pipelines.data_processor import DataProcessor
from src.pipelines.feature_engineering import FeatureEngineer
from src.training.kitchen_trainer import KitchenPerformanceTrainer
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main training function."""
    restaurant_id = int(os.getenv('RESTAURANT_ID', 1))
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # 3 months of data

    logger.info(f"Training kitchen model for restaurant {restaurant_id}")

    # Extract data
    logger.info("Extracting kitchen performance data...")
    extractor = RMSDataExtractor(os.getenv('RMS_DB_URL'))
    raw_data = extractor.extract_kitchen_performance(
        restaurant_id=restaurant_id,
        start_date=start_date.isoformat(),
        days=90
    )
    logger.info(f"Extracted {len(raw_data)} records")

    # Process data
    logger.info("Processing data...")
    processor = DataProcessor()
    clean_data = processor.process_kitchen_data(raw_data)
    logger.info(f"Processed {len(clean_data)} records")

    # Engineer features
    logger.info("Engineering features...")
    engineer = FeatureEngineer()
    X, y = engineer.create_kitchen_features(clean_data)
    logger.info(f"Created features: {X.shape}")

    # Train model
    logger.info("Training model...")
    trainer = KitchenPerformanceTrainer()
    model, metrics = trainer.train(X, y)
    logger.info(f"Training complete. Metrics: {metrics}")

    # Save model
    logger.info("Saving model...")
    trainer.save_model(model, metrics, restaurant_id)
    logger.info("Model saved successfully")

    logger.info("Training complete!")
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

### Customer Analytics Models

**File**: `scripts/train_customer_models.py`

```python
#!/usr/bin/env python
"""Train customer analytics models (churn + LTV)."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipelines.data_extractor import RMSDataExtractor
from src.pipelines.data_processor import DataProcessor
from src.pipelines.feature_engineering import FeatureEngineer
from src.training.customer_trainer import CustomerChurnTrainer, CustomerLTVTrainer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main training function."""
    restaurant_id = int(os.getenv('RESTAURANT_ID', 1))

    logger.info(f"Training customer models for restaurant {restaurant_id}")

    # Extract data
    logger.info("Extracting customer data...")
    extractor = RMSDataExtractor(os.getenv('RMS_DB_URL'))
    raw_data = extractor.extract_customer_data(restaurant_id=restaurant_id)
    logger.info(f"Extracted {len(raw_data)} customer records")

    # Process data
    logger.info("Processing data...")
    processor = DataProcessor()
    clean_data = processor.process_customer_data(raw_data)
    logger.info(f"Processed {len(clean_data)} records")

    # Engineer features
    logger.info("Engineering features...")
    engineer = FeatureEngineer()
    X = engineer.create_customer_features(clean_data)

    # Train churn model
    logger.info("Training churn model...")
    y_churn = (clean_data['days_since_last_order'] > 60).astype(int)
    churn_trainer = CustomerChurnTrainer()
    churn_model, churn_metrics = churn_trainer.train(X, y_churn)
    logger.info(f"Churn model metrics: {churn_metrics}")
    churn_trainer.save_model(churn_model, churn_metrics, restaurant_id)

    # Train LTV model
    logger.info("Training LTV model...")
    y_ltv = clean_data['total_spent']
    ltv_trainer = CustomerLTVTrainer()
    ltv_model, ltv_metrics = ltv_trainer.train(X, y_ltv)
    logger.info(f"LTV model metrics: {ltv_metrics}")
    ltv_trainer.save_model(ltv_model, ltv_metrics, restaurant_id)

    logger.info("Training complete!")
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

## Training Configuration

### Hyperparameters

**File**: `config/training_config.yaml`

```yaml
demand_forecasting:
  xgboost:
    n_estimators: 100
    max_depth: 6
    learning_rate: 0.1
    subsample: 0.8
    colsample_bytree: 0.8
    random_state: 42

  prophet:
    yearly_seasonality: true
    weekly_seasonality: true
    daily_seasonality: true
    changepoint_prior_scale: 0.05

  ensemble_weight: 0.7 # 70% XGBoost, 30% Prophet

  data:
    min_records: 1000
    train_test_split: 0.8
    validation_split: 0.1

kitchen_performance:
  lightgbm:
    n_estimators: 200
    max_depth: 8
    learning_rate: 0.05
    num_leaves: 31
    subsample: 0.8
    colsample_bytree: 0.8
    random_state: 42

  data:
    min_records: 500
    train_test_split: 0.8

customer_churn:
  xgboost:
    n_estimators: 150
    max_depth: 5
    learning_rate: 0.1
    scale_pos_weight: 3 # Handle class imbalance
    random_state: 42

  threshold: 0.5
  churn_days: 60 # Days without order = churned

  data:
    min_records: 300
    train_test_split: 0.8

customer_ltv:
  random_forest:
    n_estimators: 200
    max_depth: 10
    min_samples_split: 10
    min_samples_leaf: 5
    random_state: 42

  prediction_period_months: 12

  data:
    min_records: 300
    train_test_split: 0.8
```

## Training Schedule

### Cron Schedule

```bash
# Daily training at 2 AM
0 2 * * * cd /app && /app/venv/bin/python scripts/train_demand_model.py >> /var/log/ml-training.log 2>&1

# Daily kitchen model at 3 AM
0 3 * * * cd /app && /app/venv/bin/python scripts/train_kitchen_model.py >> /var/log/ml-training.log 2>&1

# Weekly customer models on Sunday at 4 AM
0 4 * * 0 cd /app && /app/venv/bin/python scripts/train_customer_models.py >> /var/log/ml-training.log 2>&1
```

### Celery Schedule

**File**: `src/tasks/training_tasks.py`

```python
from celery import shared_task
from celery.schedules import crontab
import subprocess
import logging

logger = logging.getLogger(__name__)

@shared_task
def train_demand_model(restaurant_id: int):
    """Train demand forecasting model."""
    logger.info(f"Starting demand model training for restaurant {restaurant_id}")

    result = subprocess.run(
        ['python', 'scripts/train_demand_model.py'],
        env={'RESTAURANT_ID': str(restaurant_id)},
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        logger.info(f"Demand model training completed for restaurant {restaurant_id}")
    else:
        logger.error(f"Demand model training failed: {result.stderr}")

    return result.returncode

@shared_task
def train_kitchen_model(restaurant_id: int):
    """Train kitchen performance model."""
    logger.info(f"Starting kitchen model training for restaurant {restaurant_id}")

    result = subprocess.run(
        ['python', 'scripts/train_kitchen_model.py'],
        env={'RESTAURANT_ID': str(restaurant_id)},
        capture_output=True,
        text=True
    )

    return result.returncode

@shared_task
def train_customer_models(restaurant_id: int):
    """Train customer analytics models."""
    logger.info(f"Starting customer models training for restaurant {restaurant_id}")

    result = subprocess.run(
        ['python', 'scripts/train_customer_models.py'],
        env={'RESTAURANT_ID': str(restaurant_id)},
        capture_output=True,
        text=True
    )

    return result.returncode

# Schedule configuration
app.conf.beat_schedule = {
    'train-demand-daily': {
        'task': 'src.tasks.training_tasks.train_demand_model',
        'schedule': crontab(hour=2, minute=0),
        'args': (1,)  # Restaurant ID
    },
    'train-kitchen-daily': {
        'task': 'src.tasks.training_tasks.train_kitchen_model',
        'schedule': crontab(hour=3, minute=0),
        'args': (1,)
    },
    'train-customer-weekly': {
        'task': 'src.tasks.training_tasks.train_customer_models',
        'schedule': crontab(hour=4, minute=0, day_of_week=0),
        'args': (1,)
    },
}
```

## Model Evaluation

### Evaluation Metrics

**File**: `src/training/evaluator.py`

```python
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)
import numpy as np
from typing import Dict

class ModelEvaluator:
    """Evaluate model performance."""

    @staticmethod
    def evaluate_regression(y_true, y_pred) -> Dict:
        """Evaluate regression model."""
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        r2 = r2_score(y_true, y_pred)
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

        return {
            'mae': float(mae),
            'rmse': float(rmse),
            'r2': float(r2),
            'mape': float(mape)
        }

    @staticmethod
    def evaluate_classification(y_true, y_pred, y_pred_proba=None) -> Dict:
        """Evaluate classification model."""
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)

        metrics = {
            'precision': float(precision),
            'recall': float(recall),
            'f1': float(f1)
        }

        if y_pred_proba is not None:
            auc_roc = roc_auc_score(y_true, y_pred_proba)
            metrics['auc_roc'] = float(auc_roc)

        return metrics

    @staticmethod
    def check_thresholds(metrics: Dict, model_type: str) -> Dict:
        """Check if metrics meet thresholds."""
        thresholds = {
            'demand': {'mae': 10, 'rmse': 15, 'r2': 0.7},
            'kitchen': {'mae': 3, 'rmse': 5, 'r2': 0.7},
            'churn': {'precision': 0.65, 'recall': 0.60, 'f1': 0.62},
            'ltv': {'mae': 100, 'r2': 0.65}
        }

        model_thresholds = thresholds.get(model_type, {})
        results = {}

        for metric, threshold in model_thresholds.items():
            if metric in metrics:
                if metric in ['mae', 'rmse', 'mape']:
                    # Lower is better
                    results[metric] = metrics[metric] <= threshold
                else:
                    # Higher is better
                    results[metric] = metrics[metric] >= threshold

        return {
            'passed': all(results.values()),
            'details': results
        }
```

### Cross-Validation

```python
from sklearn.model_selection import cross_val_score, TimeSeriesSplit

class CrossValidator:
    """Perform cross-validation."""

    @staticmethod
    def time_series_cv(model, X, y, n_splits=5):
        """Time series cross-validation."""
        tscv = TimeSeriesSplit(n_splits=n_splits)

        scores = cross_val_score(
            model, X, y,
            cv=tscv,
            scoring='neg_mean_absolute_error',
            n_jobs=-1
        )

        return {
            'mean_score': -scores.mean(),
            'std_score': scores.std(),
            'scores': -scores
        }
```

## Model Versioning

### Version Management

```python
import joblib
import json
from datetime import datetime
from pathlib import Path

class ModelVersionManager:
    """Manage model versions."""

    def __init__(self, base_path='models'):
        self.base_path = Path(base_path)

    def save_model(
        self,
        model,
        model_type: str,
        restaurant_id: int,
        metrics: Dict,
        metadata: Dict = None
    ):
        """Save model with version."""
        version = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_dir = self.base_path / model_type / f'restaurant_{restaurant_id}' / version
        model_dir.mkdir(parents=True, exist_ok=True)

        # Save model
        joblib.dump(model, model_dir / 'model.joblib')

        # Save scaler if exists
        if hasattr(model, 'scaler'):
            joblib.dump(model.scaler, model_dir / 'scaler.joblib')

        # Save metadata
        full_metadata = {
            'model_type': model_type,
            'restaurant_id': restaurant_id,
            'version': version,
            'trained_at': datetime.now().isoformat(),
            'metrics': metrics,
            **(metadata or {})
        }

        with open(model_dir / 'metadata.json', 'w') as f:
            json.dump(full_metadata, f, indent=2)

        # Update latest symlink
        latest_link = self.base_path / model_type / f'restaurant_{restaurant_id}' / 'latest'
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(version)

        return version

    def load_model(
        self,
        model_type: str,
        restaurant_id: int,
        version: str = 'latest'
    ):
        """Load model by version."""
        model_dir = self.base_path / model_type / f'restaurant_{restaurant_id}' / version

        if not model_dir.exists():
            raise FileNotFoundError(f"Model not found: {model_dir}")

        model = joblib.load(model_dir / 'model.joblib')

        # Load metadata
        with open(model_dir / 'metadata.json', 'r') as f:
            metadata = json.load(f)

        return model, metadata

    def list_versions(
        self,
        model_type: str,
        restaurant_id: int
    ) -> List[Dict]:
        """List all model versions."""
        model_dir = self.base_path / model_type / f'restaurant_{restaurant_id}'

        if not model_dir.exists():
            return []

        versions = []
        for version_dir in model_dir.iterdir():
            if version_dir.is_dir() and version_dir.name != 'latest':
                metadata_file = version_dir / 'metadata.json'
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    versions.append(metadata)

        return sorted(versions, key=lambda x: x['trained_at'], reverse=True)
```

## Automated Training Pipeline

**File**: `scripts/train_all_models.py`

```python
#!/usr/bin/env python
"""Train all models for all restaurants."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipelines.data_extractor import RMSDataExtractor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Train all models for all active restaurants."""
    # Get all active restaurants
    extractor = RMSDataExtractor(os.getenv('RMS_DB_URL'))
    restaurants = extractor.get_active_restaurants()

    logger.info(f"Found {len(restaurants)} active restaurants")

    for restaurant in restaurants:
        restaurant_id = restaurant['id']
        restaurant_name = restaurant['name']

        logger.info(f"Training models for {restaurant_name} (ID: {restaurant_id})")

        # Train demand model
        logger.info("Training demand model...")
        os.system(f"RESTAURANT_ID={restaurant_id} python scripts/train_demand_model.py")

        # Train kitchen model
        logger.info("Training kitchen model...")
        os.system(f"RESTAURANT_ID={restaurant_id} python scripts/train_kitchen_model.py")

        # Train customer models (weekly only)
        if datetime.now().weekday() == 6:  # Sunday
            logger.info("Training customer models...")
            os.system(f"RESTAURANT_ID={restaurant_id} python scripts/train_customer_models.py")

    logger.info("All training complete!")
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

---

**Next**: [Monitoring & Maintenance](./08-MONITORING.md)

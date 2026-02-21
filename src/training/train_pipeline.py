"""
Model training pipeline orchestrator.
Coordinates data extraction, processing, feature engineering, and model training.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import logging
import json
import os
from pathlib import Path

from src.pipelines.data_extractor import RMSDataExtractor
from src.pipelines.data_processor import DataProcessor, DataValidator
from src.pipelines.feature_engineering import FeatureEngineer, FeatureScaler
from src.models import (
    DemandForecastModel,
    KitchenPerformanceModel,
    CustomerChurnModel,
    CustomerLTVModel,
    InventoryOptimizationModel,
)

logger = logging.getLogger(__name__)


class ModelTrainingPipeline:
    """
    Orchestrate complete ML model training workflow.

    Handles: extraction → processing → feature engineering → training → evaluation
    """

    def __init__(
        self,
        db_url: str,
        model_dir: str = 'models',
        restaurant_id: int = 1
    ):
        """
        Initialize training pipeline.

        Args:
            db_url: PostgreSQL connection string
            model_dir: Directory to save trained models
            restaurant_id: Restaurant identifier
        """
        self.logger = logging.getLogger(__name__)
        self.db_url = db_url
        self.model_dir = model_dir
        self.restaurant_id = restaurant_id

        # Initialize components
        self.data_extractor = RMSDataExtractor(db_url)
        self.data_processor = DataProcessor()
        self.data_validator = DataValidator()
        self.feature_engineer = FeatureEngineer()

        # Create model directory
        Path(model_dir).mkdir(parents=True, exist_ok=True)

    def train_demand_model(
        self,
        days_back: int = 180,
        test_size: float = 0.2
    ) -> Dict:
        """
        Train demand forecasting model.

        Args:
            days_back: Days of historical data to use
            test_size: Fraction of data for testing

        Returns:
            Dictionary with training results
        """
        self.logger.info(f"Starting demand model training...")

        try:
            # Extract data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)

            self.logger.info(f"Extracting data from {start_date} to {end_date}...")
            raw_data = self.data_extractor.extract_orders(
                self.restaurant_id,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )

            # validate
            validation = self.data_validator.validate_orders(raw_data)
            if not validation['valid']:
                raise ValueError(f"Data validation failed: {validation['issues']}")

            # Process
            orders = self.data_processor.process_orders(raw_data)

            # Create features
            self.logger.info(f"Creating demand features...")
            X_list = []
            y_list = []
            dates_list = []

            for date in pd.date_range(start=orders['created_at'].min(), end=orders['created_at'].max(), freq='H'):
                features = self.feature_engineer.create_demand_features(orders, date)
                hourly_orders = len(orders[
                    (orders['created_at'] >= date) &
                    (orders['created_at'] < date + timedelta(hours=1))
                ])

                X_list.append(features)
                y_list.append(hourly_orders)
                dates_list.append(date)

            X = pd.DataFrame(X_list)
            y = np.array(y_list)
            dates = pd.Series(dates_list)

            # Split data
            split_idx = int(len(X) * (1 - test_size))
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            dates_train, dates_test = dates[:split_idx], dates[split_idx:]

            # Train model
            self.logger.info(f"Training demand model...")
            model = DemandForecastModel()
            model.train(X_train, y_train, dates_train)

            # Evaluate model
            metrics = model.evaluate(X_test, y_test, dates_test)

            # Save model
            self._save_model(model, 'demand', metrics)

            self.logger.info(f"Demand model training complete. Metrics: {metrics}")
            return {
                'status': 'success',
                'model_type': 'demand',
                'metrics': metrics,
                'samples': len(X)
            }

        except Exception as e:
            self.logger.error(f"Error training demand model: {e}")
            return {'status': 'error', 'error': str(e)}

    def train_kitchen_model(
        self,
        days_back: int = 90,
        test_size: float = 0.2
    ) -> Dict:
        """
        Train kitchen performance model.

        Args:
            days_back: Days of historical data to use
            test_size: Fraction of data for testing

        Returns:
            Dictionary with training results
        """
        self.logger.info(f"Starting kitchen model training...")

        try:
            # Extract data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)

            self.logger.info(f"Extracting kitchen data from {start_date} to {end_date}...")
            raw_kitchen = self.data_extractor.extract_kitchen_performance(
                self.restaurant_id,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            # Validate
            validation = self.data_validator.validate_kitchen_data(raw_kitchen)
            if not validation['valid']:
                raise ValueError(f"Data validation failed: {validation['issues']}")

            # Process
            kitchen = self.data_processor.process_kitchen_data(raw_kitchen)

            # Create features
            self.logger.info(f"Creating kitchen features...")
            X_list = []
            y_list = []

            for idx, row in kitchen.iterrows():
                features = self.feature_engineer.create_kitchen_features(
                    kitchen,
                    row['station_id'],
                    row['menu_item_id']
                )
                X_list.append(features)
                y_list.append(row['prep_time_minutes'])

            X = pd.DataFrame(X_list)
            y = np.array(y_list)

            # Split data
            split_idx = int(len(X) * (1 - test_size))
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]

            # Train model
            self.logger.info(f"Training kitchen model...")
            model = KitchenPerformanceModel()
            model.train(X_train, y_train)

            # Evaluate model
            metrics = model.evaluate(X_test, y_test)

            # Save model
            self._save_model(model, 'kitchen', metrics)

            self.logger.info(f"Kitchen model training complete. Metrics: {metrics}")
            return {
                'status': 'success',
                'model_type': 'kitchen',
                'metrics': metrics,
                'samples': len(X)
            }

        except Exception as e:
            self.logger.error(f"Error training kitchen model: {e}")
            return {'status': 'error', 'error': str(e)}

    
    def train_churn_model(
        self,
        test_size: float = 0.2
    ) -> Dict:
        """
        Train customer churn prediction model.

        Args:
            test_size: Fraction of data for testing

        Returns:
            Dictionary with training results
        """
        self.logger.info(f"Starting churn model training...")

        try:
            # Extract data
            self.logger.info(f"Extracting customer data...")
            raw_customers = self.data_extractor.extract_customer_data(self.restaurant_id)

            # Validate
            validation = self.data_validator.validate_customer_data(raw_customers)
            if not validation['valid']:
                raise ValueError(f"Data validation failed: {validation['issues']}")

            # Process
            customers = self.data_processor.process_customer_data(raw_customers)

            # Create target: churned if no order in last 60 days
            customers['churned'] = (customers['recency_days'] > 60).astype(int)

            # Create features
            self.logger.info(f"Creating churn features...")
            X_list = []
            y_list = []

            for idx, row in customers.iterrows():
                features = self.feature_engineer.create_customer_features(row)
                X_list.append(features)
                y_list.append(row['churned'])

            X = pd.DataFrame(X_list)
            y = np.array(y_list)

            # Split data
            split_idx = int(len(X) * (1 - test_size))
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]

            # Train model
            self.logger.info(f"Training churn model...")
            model = CustomerChurnModel()
            model.train(X_train, y_train, categorical_features=['current_tier'])

            # Evaluate model
            metrics = model.evaluate(X_test, y_test)

            # Save model
            self._save_model(model, 'churn', metrics)

            self.logger.info(f"Churn model training complete. Metrics: {metrics}")
            return {
                'status': 'success',
                'model_type': 'churn',
                'metrics': metrics,
                'samples': len(X),
                'churn_rate': round(y.mean() * 100, 2)
            }

        except Exception as e:
            self.logger.error(f"Error training churn model: {e}")
            return {'status': 'error', 'error': str(e)}

    def train_ltv_model(
        self,
        test_size: float = 0.2
    ) -> Dict:
        """
        Train customer lifetime value model.

        Args:
            test_size: Fraction of data for testing

        Returns:
            Dictionary with training results
        """
        self.logger.info(f"Starting LTV model training...")

        try:
            # Extract data
            self.logger.info(f"Extracting customer data...")
            raw_customers = self.data_extractor.extract_customer_data(self.restaurant_id)

            # Validate
            validation = self.data_validator.validate_customer_data(raw_customers)
            if not validation['valid']:
                raise ValueError(f"Data validation failed: {validation['issues']}")

            # Process
            customers = self.data_processor.process_customer_data(raw_customers)

            # Create target: total spent (as proxy for LTV)
            customers['ltv'] = customers['total_spent']

            # Create features
            self.logger.info(f"Creating LTV features...")
            X_list = []
            y_list = []

            for idx, row in customers.iterrows():
                features = self.feature_engineer.create_customer_features(row)
                X_list.append(features)
                y_list.append(row['ltv'])

            X = pd.DataFrame(X_list)
            y = np.array(y_list)

            # Split data
            split_idx = int(len(X) * (1 - test_size))
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]

            # Train model
            self.logger.info(f"Training LTV model...")
            model = CustomerLTVModel()
            model.train(X_train, y_train, categorical_features=['current_tier'])

            # Evaluate model
            metrics = model.evaluate(X_test, y_test)

            # Save model
            self._save_model(model, 'ltv', metrics)

            self.logger.info(f"LTV model training complete. Metrics: {metrics}")
            return {
                'status': 'success',
                'model_type': 'ltv',
                'metrics': metrics,
                'samples': len(X),
                'avg_ltv': round(y.mean(), 2)
            }

        except Exception as e:
            self.logger.error(f"Error training LTV model: {e}")
            return {'status': 'error', 'error': str(e)}

    def train_inventory_model(
        self,
        days_back: int = 90
    ) -> Dict:
        """
        Train inventory optimization model.

        Args:
            days_back: Days of historical data to use

        Returns:
            Dictionary with training results
        """
        self.logger.info(f"Starting inventory model training...")

        try:
            # Extract data
            self.logger.info(f"Extracting inventory data...")
            raw_inventory = self.data_extractor.extract_inventory_data(self.restaurant_id)

            # Validate
            validation = self.data_validator.validate_inventory_data(raw_inventory)
            if not validation['valid']:
                raise ValueError(f"Data validation failed: {validation['issues']}")

            # Process
            inventory = self.data_processor.process_inventory_data(raw_inventory)

            # Train model
            self.logger.info(f"Training inventory model...")
            model = InventoryOptimizationModel()
            model.train(inventory)

            # Save model
            self._save_model(model, 'inventory', {})

            self.logger.info(f"Inventory model training complete.")
            return {
                'status': 'success',
                'model_type': 'inventory',
                'samples': len(inventory)
            }

        except Exception as e:
            self.logger.error(f"Error training inventory model: {e}")
            return {'status': 'error', 'error': str(e)}

    def train_all_models(self) -> Dict:
        """
        Train all models sequentially.

        Returns:
            Dictionary with training results
        """
        self.logger.info("Starting complete model training pipeline...")

        results = {
            'timestamp': datetime.now().isoformat(),
            'restaurant_id': self.restaurant_id,
            'models': []
        }

        # Train each model
        results['models']['demand'] = self.train_demand_model()
        results['models']['kitchen'] = self.train_kitchen_model()
        results['models']['churn'] = self.train_churn_model()
        results['models']['ltv'] = self.train_ltv_model()
        results['models']['inventory'] = self.train_inventory_model()

        # Summary
        successful = sum(1 for m in results['models'] if m['status'] == 'success')
        results['summary'] = {
            'total_models': len(results['models']),
            'successful': successful,
            'failed': len(results['models']) - successful
        }

    def _save_model(
        self,
        model,
        model_type: str,
        metrics: Dict
    ):
        """
        Save trained model with metadata

        Args:
            model: Trained model instance
            model_type: Type of model
            metrics: Evaluation metrics
        """
        import joblib

        # Create versioned directory
        version = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_path = os.path.join(
            self.model_dir,
            model_type,
            f'restaurant_{self.restaurant_id}',
            version
        )
        os.makedirs(model_path, exist_ok=True)

        # Save model
        model_file = os.path.join(model_path, 'model.joblib')
        joblib.dump(model, model_file)

        # Save metadata
        metadata = {
            'model_type': model_type,
            'restaurant_id': self.restaurant_id,
            'version': version,
            'trained_at': datetime.now().isoformat(),
            'metrics': metrics
        }

        metadata_file = os.path.join(model_path, 'metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Update latest symlink
        latest_link = os.path.join(
            self.model_dir,
            model_type,
            f'restaurant_{self.restaurant_id}',
            'latest'
        )

        if os.path.exists(latest_link):
            os.remove(latest_link)

        os.symlink(model_path, latest_link)

        self.logger.info(f"Model saved to {model_path}. Latest version: {version}")

    def close(self):
        """Close database connection"""
        self.data_extractor.close()
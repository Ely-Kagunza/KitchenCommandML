"""
Demand forecasting prediction service.
Loads trained model and generates demand predictions.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import joblib
import logging
import os

from src.pipelines.feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)


class DemandPredictionService:
    """
    Service for generating demand predictions.

    Loads trained demand model and generates hourly/daily forecasts.
    """

    def __init__(self, model_path: str):
        """
        Initialize demand prediction service.

        Args:
            model_path: Path to trained demand model directory
        """
        self.logger = logging.getLogger(__name__)
        self.model_path = model_path
        self.model = None
        self.feature_engineer = FeatureEngineer()

        self._load_model()

    def _load_model(self):
        """Load trained model from disk."""
        try:
            model_file = os.path.join(self.model_path, 'model.joblib')
            self.model = joblib.load(model_file)
            self.logger.info(f"Loaded demand model from {model_file}")
        except Exception as e:
            self.logger.error(f"Error loading demand model: {e}")
            raise

    def predict_hourly(
        self,
        historical_orders: pd.DataFrame,
        hours_ahead: int = 24
    ) -> Dict:
        """
        Predict hourly demand for next N hours.

        Args:
            historical_orders: Historical order data
            hours_ahead: Number of hours to forecast

        Returns:
            Dictionary with predictions
        """
        predictions = []
        now = datetime.now()

        for i in range(hours_ahead):
            target_time = now + timedelta(hours=i)

            # Create features
            features = self.feature_engineer.create_demand_features(
                historical_orders,
                target_time
            )

            # Predict
            X = pd.DataFrame([features])
            pred = self.model.predict(X, pd.Series([target_time]))[0]

            predictions.append({
                'timestamp': target_time.isoformat(),
                'hour': target_time.hour,
                'predicted_orders': max(int(pred), 0),
                'confidence': 0.85
            })

        return {
            'forecast_type': 'hourly',
            'hours_ahead': hours_ahead,
            'predictions': predictions,
            'generated_at': datetime.now().isoformat()
        }

    def predict_daily(
        self,
        historical_orders: pd.DataFrame,
        days_ahead: int = 7
    ) -> Dict:
        """
        Predict daily demand for next N days.

        Args:
            historical_orders: Historical order data
            days_ahead: Number of days to forecast

        Returns:
            Dictionary with predictions
        """
        predictions = []
        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        for i in range(days_ahead):
            target_date = now + timedelta(days=i)

            # Predict for each hour of the day
            daily_predictions = []
            daily_total = 0

            for hour in range(24):
                target_time = target_date.replace(hour=hour)

                features = self.feature_engineer.create_demand_features(
                    historical_orders,
                    target_time
                )

                X = pd.DataFrame([features])
                pred = self.model.predict(X, pd.Series([target_time]))[0]
                daily_predictions.append(max(int(pred), 0))
                daily_total += pred

            predictions.append({
                'date': target_date.date().strftime('%Y-%m-%d'),
                'day_of_week': target_date.strftime('%A'),
                'predicted_orders': max(int(daily_total), 0),
                'hourly_breakdown': daily_predictions,
                'confidence': 0.80
            })

        return {
            'forecast_type': 'daily',
            'days_ahead': days_ahead,
            'predictions': predictions,
            'generated_at': datetime.now().isoformat()
        }

    def predict_item_demand(
        self,
        historical_orders: pd.DataFrame,
        item_id: int,
        hours_ahead: int = 24
    ) -> Dict:
        """
        Predict demand for specific menu item.

        Args:
            historical_orders: Historical order data
            item_id: Menu item ID
            hours_ahead: Number of hours to forecast

        Returns:
            Dictionary with item-level predictions
        """
        # Filter for specific item
        item_orders = historical_orders[historical_orders['menu_item_id'] == item_id]

        if len(item_orders) == 0:
            return {
                'item_id': item_id,
                'error': 'No historical data for item'
            }

        # Get item name
        item_name = item_orders['item_name'].iloc[0] if len(item_orders) > 0 else 'Unknown'

        predictions = []
        now = datetime.now()

        for i in range(hours_ahead):
            target_time = now + timedelta(hours=i)

            # Create features
            features = self.feature_engineer.create_demand_features(
                item_orders,
                target_time
            )

            # Predict
            X = pd.DataFrame([features])
            pred = self.model.predict(X, pd.Series([target_time]))[0]

            predictions.append({
                'timestamp': target_time.isoformat(),
                'predicted_orders': max(int(pred), 0)
            })

        return {
            'item_id': item_id,
            'item_name': item_name,
            'forecast_type': 'item_hourly',
            'hours_ahead': hours_ahead,
            'predictions': predictions,
            'generated_at': datetime.now().isoformat()
        }

    def predict_category_demand(
        self,
        historical_orders: pd.DataFrame,
        category_name: str,
        hours_ahead: int = 24
    ) -> Dict:
        """
        Predict demand for menu category

        Args:
            historical_orders: Historical order data
            category_name: Menu category name
            hours_ahead: Number of hours to forecast

        Returns:
            Dictionary with category-level predictions
        """
        # Filter for category
        category_orders = historical_orders[
            historical_orders['category_name'] == category_name
        ]

        if len(category_orders) == 0:
            return {
                'category_name': category_name,
                'error': 'No historical data for category'
            }

        predictions = []
        now = datetime.now()

        for i in range(hours_ahead):
            target_time = now + timedelta(hours=i)

            features = self.feature_engineer.create_demand_features(
                category_orders,
                target_time
            )

            X = pd.DataFrame([features])
            pred = self.model.predict(X, pd.Series([target_time]))[0]

            predictions.append({
                'timestamp': target_time.isoformat(),
                'predicted_orders': max(int(pred), 0)
            })

        return {
            'category': category_name,
            'forecast_type': 'category_hourly',
            'hours_ahead': hours_ahead,
            'predictions': predictions,
            'generated_at': datetime.now().isoformat()
        }

    def get_peak_hours(
        self,
        historical_orders: pd.DataFrame,
        days_ahead: int = 7
    ) -> Dict:
        """
        Identify peak hours for next N days.

        Args:
            historical_orders: Historical order data
            days_ahead: Number of days to forecast

        Returns:
            Dictionary with peak hours
        """
        peak_analysis = []
        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        for i in range(days_ahead):
            target_date = now + timedelta(days=i)

            hourly_predictions = []

            for hour in range(24):
                target_time = target_date.replace(hour=hour)

                features = self.feature_engineer.create_demand_features(
                    historical_orders,
                    target_time
                )

                X = pd.DataFrame([features])
                pred = self.model.predict(X, pd.Series([target_time]))[0]
                hourly_predictions.append(max(int(pred), 0))

            # Find peak hours (top 3)
            hourly_with_hours = [(hour, pred) for hour, pred in enumerate(hourly_predictions)]
            hourly_with_hours.sort(key=lambda x: x[1], reverse=True)
            peak_hours = hourly_with_hours[:3]

            peak_analysis.append({
                'date': target_date.strftime('%Y-%m-%d'),
                'peak_hours': [
                    {
                        'hour': int(h),
                        'predicted_orders': int(p)
                    }
                    for h, p in peak_hours
                ]
            })

        return {
            'analysis_type': 'peak_hours',
            'days_ahead': days_ahead,
            'analysis': peak_analysis,
            'generated_at': datetime.now().isoformat()
        }
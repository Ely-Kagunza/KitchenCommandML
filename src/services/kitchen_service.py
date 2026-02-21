"""
Kitchen performance prediction service.
Predicts preparation times for menu items.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional
import joblib
import logging
import os

from pandas.core.nanops import bottleneck_switch

from src.pipelines.feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)


class KitchenPredictionService:
    """
    Service for predicting kitchen prep times.

    Estimates how long items take to prepare at specific stations.
    """

    def __init__(self, model_path: str):
        """
        Initialize kitchen prediction service.

        Args:
            model_path: Path to trained kitchen model directory
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
            self.logger.info(f"Loaded kitchen model from {model_file}")
        except Exception as e:
            self.logger.error(f"Error loading kitchen model: {e}")
            raise

    def predict_prep_time(
        self,
        station_id: int,
        menu_item_id: int,
        historical_kitchen_data: pd.DataFrame
    ) -> Dict:
        """
        Predict prep time for item at station.

        Args:
            station_id: Kitchen station ID
            menu_item_id: Menu item ID
            historical_kitchen_data: Historical kitchen data

        Returns:
            Dictionary with prep time prediction
        """
        # Create features
        features = self.feature_engineer.create_kitchen_features(
            historical_kitchen_data,
            station_id,
            menu_item_id
        )

        # Predict
        X = pd.DataFrame([features])
        pred_result = self.model.predict_with_confidence(X)

        return {
            'station_id': station_id,
            'menu_item_id': menu_item_id,
            'predicted_prep_time_minutes': round(pred_result['prediction'][0], 1),
            'lower_bound_minutes': round(pred_result['lower_bound'][0], 1),
            'upper_bound_minutes': round(pred_result['upper_bound'][0], 1),
            'confidence': 0.85
        }

    def predict_batch_prep_time(
        self,
        orders: List[Dict],
        historical_kitchen_data: pd.DataFrame
    ) -> Dict:
        """
        Predict prep times for batch of orders

        Args:
            orders: List of order dicts with station_id and menu_item_id
            historical_kitchen_data: Historical kitchen data

        Returns:
            Dictionary with batch prep time predictions
        """
        predictions = []

        for order in orders:
            pred = self.predict_prep_time(
                order['station_id'],
                order['menu_item_id'],
                historical_kitchen_data
            )
            predictions.append(pred)

        # calculate total time (max of all items)
        total_time = max([p['predicted_prep_time_minutes'] for p in predictions])

        return {
            'batch_size': len(orders),
            'item_predictions': predictions,
            'estimated_total_time_minutes': total_time,
            'generated_at': pd.Timestamp.now().isoformat()
        }

    def identify_bottlenecks(
        self,
        historical_kitchen_data: pd.DataFrame,
        threshold_percentile: float = 75
    ) -> Dict:
        """
        Identify kitchen bottlenecks.

        Args:
            historical_kitchen_data: Historical kitchen data
            threshold_percentile: Percentile threshold for bottleneck detection

        Returns:
            Dictionary with bottleneck analysis
        """
        bottlenecks = []

        # Group by station
        for station_id in historical_kitchen_data['station_id'].unique():
            station_data = historical_kitchen_data[
                historical_kitchen_data['station_id'] == station_id
            ]

            avg_prep_time = station_data['prep_time_minutes'].mean()
            threshold = np.percentile(
                station_data['prep_time_minutes'],
                threshold_percentile
            )

            # Items above threshold
            slow_items = station_data[
                station_data['prep_time_minutes'] > threshold
            ].groupby('menu_item_id').agg({
                'prep_time_minutes': ['mean', 'count']
            }).reset_index()

            if len(slow_items) > 0:
                bottlenecks.append({
                    'station_id': int(station_id),
                    'station_name': station_data['station_name'].iloc[0],
                    'avg_prep_time': round(avg_prep_time, 1),
                    'bottleneck_threshold': round(threshold, 1),
                    'slow_items': [
                        {
                            'menu_item_id': int(row[1][0]),
                            'avg_prep_time': round(row[1][1][0], 1),
                            'occurences': int(row[1][1][1])
                        }
                        for row in slow_items.iterrows()
                    ]
                })

        return {
            'analysis_type': 'bottleneck_detection',
            'bottlenecks': bottlenecks,
            'generated_at': pd.Timestamp.now().isoformat()
        }

    def get_station_performance(
        self,
        historical_kitchen_data: pd.DataFrame
    ) -> Dict:
        """
        Get performance metrics for each station.

        Args:
            historical_kitchen_data: Historical kitchen data

        Returns:
            Dictionary with station performance metrics
        """
        station_metrics = []

        for station_id in historical_kitchen_data['station_id'].unique():
            station_data = historical_kitchen_data[
                historical_kitchen_data['station_id'] == station_id
            ]

            metrics = {
                'station_id': int(station_id),
                'station_name': station_data['station_name'].iloc[0],
                'total_items_prepared': len(station_data),
                'avg_prep_time_minutes': round(station_data['prep_time_minutes'].mean(), 1),
                'median_prep_time_minutes': round(station_data['prep_time_minutes'].median(), 1),
                'std_dev_prep_time': round(station_data['prep_time_minutes'].std(), 1),
                'min_prep_time': round(station_data['prep_time_minutes'].min(), 1),
                'max_prep_time': round(station_data['prep_time_minutes'].max(), 1),
                'within_5_min_accuracy': round(
                    (station_data['prep_time_minutes'] <= 5).sum() / len(station_data) * 100,
                    1
                )
            }

            station_metrics.append(metrics)

        return {
            'analysis_type': 'station_performance',
            'stations': station_metrics,
            'generated_at': pd.Timestamp.now().isoformat()
        }

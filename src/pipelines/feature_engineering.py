"""
Feature engineering module for creating ML-ready features.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Create ML features from processed data."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_demand_features(
        self,
        df: pd.DataFrame,
        target_date: datetime
    ) -> Dict:
        """
        Create features for demand forecasting.

        Features:
        - Time-based: hour, day_of_week, month, is_weekend, is_holiday
        - Lag features: orders 1/7/30 days ago
        - Rolling averages: 7-day, 30-day moving averages
        - Trend: linear trend over time
        - Seasonality: cyclical encoding of time features

        Args:
            df: Processed order DataFrame
            target_date: Date to create features for

        Returns:
            Dictionary of features
        """
        features = {}

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
        if len(df) > 0:
            first_order_date = df['created_at'].min()
            features['days_since_start'] = (target_date - first_order_date).days
        else:
            features['days_since_start'] = 0

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
        - Item characteristics: complexity, historical performance
        - Station load: current queue size
        - Historical performance: avg prep time for item/station
        - Time context: hour, day_of_week
        - Complexity: variance in prep time

        Args:
            df: Processed kitchen DataFrame
            station_id: Kitchen station ID
            menu_item_id: Menu item ID

        Returns:
            Dictionary of features
        """
        features = {}

        # Filter for specific station and item
        item_station_df = df[
            (df['station_id'] == station_id) &
            (df['menu_item_id'] == menu_item_id)
        ]

        # Historical averages
        if len(item_station_df) > 0:
            features['avg_prep_time'] = item_station_df['prep_time_minutes'].mean()
            features['std_prep_time'] = item_station_df['prep_time_minutes'].std()
            features['min_prep_time'] = item_station_df['prep_time_minutes'].min()
            features['max_prep_time'] = item_station_df['prep_time_minutes'].max()
            features['median_prep_time'] = item_station_df['prep_time_minutes'].median()
        else:
            # Use station averages if no item history
            station_df = df[df['station_id'] == station_id]
            if len(station_df) > 0:
                features['avg_prep_time'] = station_df['prep_time_minutes'].mean()
                features['std_prep_time'] = station_df['prep_time_minutes'].std()
                features['min_prep_time'] = station_df['prep_time_minutes'].min()
                features['max_prep_time'] = station_df['prep_time_minutes'].max()
                features['median_prep_time'] = station_df['prep_time_minutes'].median()
            else:
                # Default values
                features['avg_prep_time'] = 10.0
                features['std_prep_time'] = 2.0
                features['min_prep_time'] = 5.0
                features['max_prep_time'] = 20.0
                features['median_prep_time'] = 10.0

        # Item complexity (based on historical variance)
        if features['avg_prep_time'] > 0:
            features['item_complexity'] = features['std_prep_time'] / features['avg_prep_time']
        else:
            features['item_complexity'] = 0.0

        return features

    def create_customer_features(
        self,
        customer_row: pd.Series
    ) -> Dict:
        """
        Create features for customer analytics.

        Features:
        - RFM: Recency, Frequency, Monetary
        - Loyalty: current tier, points, lifetime value
        - Behavior: avg order value, order frequency
        - Engagement: days since signup, total orders

        Args:
            customer_row: Single customer row from DataFrame

        Returns:
            Dictionary of features
        """
        features = {
            # RFM
            'recency_days': customer_row['recency_days'],
            'frequency': customer_row['frequency'],
            'monetary': customer_row['monetary'],

            # Loyalty
            'current_points': customer_row['current_points'],
            'lifetime_points': customer_row['lifetime_points'],
            'current_tier': customer_row['current_tier'],

            # Behavior
            'avg_order_value': customer_row['avg_order_value'],
            'days_since_signup': customer_row['days_since_signup'],
            'order_frequency': customer_row['order_frequency'],

            # Engagement
            'unique_order_days': customer_row['unique_order_days'],
        }

        # Calculate RFM score (1-5 scale)
        features['rfm_score'] = self._calculate_rfm_score(
            features['recency_days'],
            features['frequency'],
            features['monetary']
        )

        return features

    def create_inventory_features(
        self,
        inventory_row: pd.Series
    ) -> Dict:
        """
        Create features for inventory optimization.

        Features:
        - Stock levels: current, min, reorder
        - Consumption: daily, last 30 days
        - Status: days until stockout, stock status
        - Cost: unit cost, holding cost

        Args:
            inventory_row: Single inventory row from DataFrame

        Returns:
            Dictionary of features
        """
        features = {
            'current_stock': inventory_row['current_stock'],
            'min_level': inventory_row['min_level'],
            'reorder_level': inventory_row['reorder_level'],
            'daily_consumption_rate': inventory_row['daily_consumption_rate'],
            'consumption_last_30_days': inventory_row['consumption_last_30_days'],
            'avg_unit_cost': inventory_row['avg_unit_cost'],
            'stock_status': inventory_row['stock_status'],
            'days_until_stockout': inventory_row['days_until_stockout'],
            'batch_count': inventory_row['batch_count'],
        }

        # Calculate stock ratio
        if inventory_row['reorder_level'] > 0:
            features['stock_to_reorder_ratio'] = (
                inventory_row['current_stock'] / inventory_row['reorder_level']
            )
        else:
            features['stock_to_reorder_ratio'] = 1.0

        # calculate urgency (how soon to reorder)
        if inventory_row['daily_consumption_rate'] > 0:
            features['days_until_reorder'] = (
                (inventory_row['current_stock'] - inventory_row['reorder_level']) / inventory_row['daily_consumption_rate']
            )
        else:
            features['days_until_reorder'] = 999

        return features

    def create_payment_features(
        self,
        df: pd.DataFrame,
        target_date: datetime
    ) -> Dict:
        """
        Create features for payment analytics.

        Features:
        - Payment method: credit/debit, cash, other
        - Tip amount: average, variance
        - Payment timing: hour of day, day of week
        - Average transaction value

        Args:
            df: Processed payment DataFrame
            target_date: Date to create features for

        Returns:
            Dictionary of features
        """
        features = {}

        # Time-based features
        features['hour'] = target_date.hour
        features['day_of_week'] = target_date.weekday()
        features['is_weekend'] = int(target_date.weekday() >= 5)
        features['is_peak_hour'] = int(target_date.hour in [12, 13, 18, 19, 20])

        # Payment method distribution (last 30 days)
        thirty_days_ago = target_date - timedelta(days=30)
        recent_payments = df[df['created_at'] >= thirty_days_ago]

        if len(recent_payments) > 0:
            payment_methods = recent_payments['payment_method'].value_counts()
            for method, count in payment_methods.items():
                features[f'payment_method_{method}_pct'] = (count / len(recent_payments)) * 100

            # Tip statistics
            features['avg_tip_amount'] = recent_payments['tip_amount'].mean()
            features['avg_tip_percentage'] = recent_payments['tip_amount'].mean()
            features['avg_transaction_value'] = recent_payments['amount'].mean()
        else:
            features['avg_tip_amount'] = 0.0
            features['avg_tip_percentage'] = 0.0
            features['avg_transaction_value'] = 0.0

        return features

    # Helper methods
    def _get_orders_at_time(
        self,
        df: pd.DataFrame,
        target_time: datetime
    ) -> int:
        """
        Get order count at specific time.

        Args:
            df: Order DataFrame
            target_time: Target datetime

        Returns:
            Number od orders at that time
        """
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
        """
        Calculate rolling average of orders.

        Args:
            df: Order DataFrame
            target_time: Target datetime
            days: Number of days to average

        Returns:
            Average orders per hour over period
        """
        start_time = target_time - timedelta(days=days)
        period_df = df[
            (df['created_at'] >= start_time) &
            (df['created_at'] < target_time)
        ]

        if len(period_df) == 0:
            return 0.0

        # Group by hour and calculate average
        hourly_counts = period_df.groupby(
            period_df['created_at'].dt.floor('H')
        ).size()

        return float(hourly_counts.mean()) if len(hourly_counts) > 0 else 0.0

    def _calculate_rfm_score(
        self,
        recency: float,
        frequency: float,
        monetary: float
    ) -> float:
        """
        Calculate RFM score (1-5 scale).

        Higher scores = better customer.

        Args:
            recency: Days since last order
            frequency: Total orders
            monetary: Total spent

        Returns:
            RFM score (1-5)
        """
        # Recency score (lower is better)
        if recency <= 30:
            recency_score = 5
        elif recency <= 60:
            recency_score = 4
        elif recency <= 90:
            recency_score = 3
        elif recency <= 180:
            recency_score = 2
        else:
            recency_score = 1

        # Frequency score (higher is better)
        if frequency >= 20:
            frequency_score = 5
        elif frequency >= 10:
            frequency_score = 4
        elif frequency >= 5:
            frequency_score = 3
        elif frequency >= 2:
            frequency_score = 2
        else:
            frequency_score = 1

        # Monetary score (higher is better)
        if monetary >= 1000:
            monetary_score = 5
        elif monetary >= 500:
            monetary_score = 4
        elif monetary >= 200:
            monetary_score = 3
        elif monetary >= 50:
            monetary_score = 2
        else:
            monetary_score = 1

        # Average RFM score
        rfm_score = (recency_score + frequency_score + monetary_score) / 3

        return round(rfm_score, 2)

class FeatureScaler:
    """ Scale features for ML models."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scaler = {}

    def fit_scaler(
        self,
        feature_name: str,
        values: np.ndarray
    ):
        """
        Fit a scaler for a feature.

        Args:
            feature_name: Name of the feature
            values: Array of values to fit on
        """
        from sklearn.preprocessing import StandardScaler

        scaler = StandardScaler()
        scaler.fit(values.reshape(-1, 1))
        self.scaler[feature_name] = scaler

    def scale_feature(
        self,
        feature_name: str,
        value: float
    ) -> float:
        """
        Scale a single feature value.

        Args:
            feature_name: Name of the feature
            value: Value to scale
        
        Returns:
            Scaled value
        """
        if feature_name not in self.scaler:
            return value
        
        scaler = self.scaler[feature_name]
        scaled = scaler.transform([[value]])[0][0]
        return float(scaled)

    def scale_features(
        self,
        features: Dict,
        numeric_features: List[str]
    ) -> Dict:
        """
        Scale multiple features

        Args:
            features: Dictionary of features
            numeric_features: List of feature names to scale

        Returns:
            Dictionary of scaled features
        """
        scaled_features = features.copy()

        for feature_name in numeric_features:
            if feature_name in scaled_features:
                scaled_features[feature_name] = self.scale_feature(
                    feature_name, 
                    scaled_features[feature_name]
                )

        return scaled_features


class FeatureStore:
    """Store and retrieve cached features."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = {}

    def store_features(
        self,
        key: str,
        features: Dict,
        ttl_seconds: int = 3600
    ):
        """
        Store features in cache.

        Args:
            key: Cache key
            features: Dictionary of features
            ttl_seconds: Time to live in seconds
        """
        self.cache[key] = {
            'features': features,
            'timestamp': datetime.now(),
            'ttl': ttl_seconds
        }

    def get_features(self, key: str) -> Dict:
        """
        Retrieve features from cache.

        Args:
            key: Cache key

        Returns:
            Features dictionary or None if not found
        """
        if key not in self.cache:
            return None

        cached = self.cache[key]
        age = (datetime.now() - cached['timestamp']).total_seconds()

        if age > cached['ttl']:
            del self.cache[key]
            return None

        return cached['features']

    def clear_cache(self):
        """Clear all cached features."""
        self.cache.clear()

    def cleanup_expired(self):
        """Remove expired entries from cache."""
        expired_keys = []

        for key, cached in self.cache.items():
            age = (datetime.now() - cached['timestamp']).total_seconds()
            if age > cached['ttl']:
                expired_keys.append(key)

        for key in expired_keys:
            del self.cache[key]

        return len(expired_keys)
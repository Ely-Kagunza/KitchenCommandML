"""
Data processing module for cleaning and validating extracted data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """Clean and validate extracted data."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_orders(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate order data.

        Steps:
        1. Convert timestamps
        2. Handle missing values
        3. Remove invalid records
        4. Remove outliers
        5. Create derived fields

        Args:
            df: Raw Order DataFrame

        Returns:
            Cleaned Order DataFrame
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
        df = df[df['unit_price'] > 0]

        # Remove outliers (orders > 3 std dev from mean)
        mean_total = df['grand_total'].mean()
        std_total = df['grand_total'].std()
        df = df[
            (df['grand_total'] >= mean_total - 3*std_total) &
            (df['grand_total'] <= mean_total + 3*std_total)
        ]

        # Create derived fields
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_peak_hour'] = df['hour_of_day'].isin([12, 13, 18, 19, 20]).astype(int)
        df['order_date'] = df['created_at'].dt.date

        self.logger.info(f"Processed {len(df)} order records")
        return df

    def process_kitchen_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate kitchen performance data.

        Steps:
        1. Convert timestamps
        2. Remove records with missing timing
        3. Remove negative or zero times (data errors)
        4. Remove extreme outliers (> 2 hours prep time)
        5. Handle queue time edge cases

        Args:
            df: Raw Kitchen Performance DataFrame

        Returns:
            Cleaned Kitchen Performance DataFrame
        """
        # Make a copy
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

        # Create derived fields
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_peak_hour'] = df['hour_of_day'].isin([12, 13, 18, 19, 20]).astype(int)

        self.logger.info(f"Processed {len(df)} kitchen performance records")
        return df

    def process_customer_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate customer data.

        Steps:
        1. Convert timestamps
        2. Handle missing values
        3. Remove customers with no orders
        4. Calculate RFM metrics

        Args:
            df: Raw Customer Data DataFrame

        Returns:
            Cleaned Customer Data DataFrame
        """
        # Make a copy
        df = df.copy()

        # Convert timestamps
        df['customer_since'] = pd.to_datetime(df['customer_since'])
        df['last_order_date'] = pd.to_datetime(df['last_order_date'])

        # Handle missing values
        df['total_orders'] = df['total_orders'].fillna(0).astype(int)
        df['total_spent'] = df['total_spent'].fillna(0)
        df['current_points'] = df['current_points'].fillna(0).astype(int)
        df['current_tier'] = df['current_tier'].fillna('bronze')
        df['unique_order_days'] = df['unique_order_days'].fillna(0).astype(int)

        # Remove customers with no orders
        df = df[df['total_orders'] > 0]

        # Calculate recency, frequency, monetary (RFM)
        df['recency_days'] = df['days_since_last_order'].fillna(999)
        df['frequency'] = df['total_orders']
        df['monetary'] = df['total_spent']

        # Calculate order frequency (orders per active day)
        df['order_frequency'] = df.apply(
            lambda row: row['total_orders'] / max(row['unique_order_days'], 1),
            axis=1
        )

        self.logger.info(f"Processed {len(df)} customer records")
        return df

    def process_inventory_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate inventory data.

        Steps:
        1. Handle missing values
        2. Calculate consumption rate
        3. Calculate stock status
        4. Calculate days until stockout

        Args:
            df: Raw Inventory Data DataFrame

        Returns:
            Cleaned Inventory Data DataFrame
        """
        # Make a copy
        df = df.copy()

        # Handle missing values
        df['current_stock'] = df['current_stock'].fillna(0)
        df['consumption_last_30_days'] = df['consumption_last_30_days'].fillna(0)
        df['batch_count'] = df['batch_count'].fillna(0).astype(int)
        df['avg_unit_cost'] = df['avg_unit_cost'].fillna(0)

        # Calculate consumption rate
        df['daily_consumption_rate'] = df['consumption_last_30_days'] / 30

        # Calculate stock status
        def get_stock_status(row):
            if row['current_stock'] <= row['min_level']:
                return 'low'
            elif row['current_stock'] <= row['reorder_level']:
                return 'medium'
            else:
                return 'high'

        df['stock_status'] = df.apply(get_stock_status, axis=1)

        # Calculate days until stockout
        def get_days_until_stockout(row):
            if row['daily_consumption_rate'] > 0:
                return row['current_stock'] / row['daily_consumption_rate']
            else:
                return np.inf

        df['days_until_stockout'] = df.apply(get_days_until_stockout, axis=1)

        self.logger.info(f"Processed {len(df)} inventory records")
        return df

    def process_payment_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate payment data.

        Steps:
        1. Convert timestamps
        2. Handle missing values
        3. Remove invalid records
        4. Create derived fields

        Args:
            df: Raw Payment Data DataFrame

        Returns:
            Cleaned Payment Data DataFrame
        """
        # Make a copy
        df = df.copy()

        # Convert timestamps
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['completed_at'] = pd.to_datetime(df['completed_at'])

        # Handle missing values
        df['tip_amount'] = df['tip_amount'].fillna(0)
        df['payment_method'] = df['payment_method'].fillna('unknown')

        # Remove invalid records
        df = df[df['amount'] > 0]
        df = df[df['status'].isin(['completed', 'paid'])]

        # Create derived fields
        df['tip_percentage'] = (df['tip_amount'] / df['amount'] * 100).round(2)
        df['is_peak_hour'] = df['hour_of_day'].isin([12, 13, 18, 19, 20]).astype(int)
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

        self.logger.info(f"Processed {len(df)} payment records")
        return df


class DataValidator:
    """Validate data quality."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def validate_orders(self, df: pd.DataFrame) -> Dict:
        """
        Validate order data quality.

        Args:
            df: Raw Order DataFrame

        Returns:
            Validation results dictionary
        """
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

    def validate_kitchen_data(self, df: pd.DataFrame) -> Dict:
        """Validate kitchen data quality."""
        issues = []

        required_cols = ['station_id', 'assigned_at', 'completed_at', 'prep_time_minutes']
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            issues.append(f"Missing columns: {missing_cols}")

        if (df['prep_time_minutes'] < 0).any():
            issues.append("Negative prep_time_minutes values found")

        return {
          'valid': len(issues) == 0,
          'issues': issues,
          'record_count': len(df)
        }

    def validate_customer_data(self, df: pd.DataFrame) -> Dict:
        """Validate customer data quality."""
        issues = []

        required_cols = ['customer_id', 'total_orders', 'total_spent']
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            issues.append(f"Missing columns: {missing_cols}")

        if (df['total_orders'] < 0).any():
            issues.append("Negative total_orders values found")

        if (df['total_spent'] < 0).any():
            issues.append("Negative total_spent values found")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'record_count': len(df)
        }

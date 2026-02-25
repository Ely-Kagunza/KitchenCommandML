"""
Unit tests for feature engineering.
"""

import pytest
from datetime import datetime
import pandas as pd


class TestFeatureEngineering:
    """Tests for feature engineering functions."""
    
    def test_time_features_extraction(self):
        """Test extraction of time-based features."""
        test_time = datetime(2024, 1, 15, 14, 30)
        
        # Extract features
        hour = test_time.hour
        day_of_week = test_time.weekday()
        is_weekend = day_of_week >= 5
        
        assert hour == 14
        assert day_of_week == 0  # Monday
        assert is_weekend is False
    
    def test_weekend_detection(self):
        """Test weekend detection."""
        # Saturday
        saturday = datetime(2024, 1, 13, 12, 0)
        assert saturday.weekday() == 5
        
        # Sunday
        sunday = datetime(2024, 1, 14, 12, 0)
        assert sunday.weekday() == 6
        
        # Monday
        monday = datetime(2024, 1, 15, 12, 0)
        assert monday.weekday() == 0
    
    def test_hour_of_day_features(self):
        """Test hour of day categorization."""
        morning = datetime(2024, 1, 15, 8, 0)
        lunch = datetime(2024, 1, 15, 12, 0)
        dinner = datetime(2024, 1, 15, 19, 0)
        
        assert morning.hour == 8
        assert lunch.hour == 12
        assert dinner.hour == 19
    
    def test_aggregation_features(self, sample_orders_data):
        """Test aggregation of order features."""
        # Group by hour
        hourly_agg = sample_orders_data.groupby(
            sample_orders_data['order_time'].dt.hour
        )['quantity'].sum()
        
        assert len(hourly_agg) > 0
        assert hourly_agg.sum() == sample_orders_data['quantity'].sum()

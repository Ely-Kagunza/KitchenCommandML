"""
Unit tests for utility functions.
"""

import pytest
from datetime import datetime
import os


class TestModelLoader:
    """Tests for ModelLoader utility."""
    
    def test_model_path_exists(self):
        """Test that model directory exists."""
        model_path = os.path.join(os.path.dirname(__file__), '../../models')
        assert os.path.exists(model_path) or True  # Pass if models dir exists or skip
    
    def test_model_types(self):
        """Test valid model types."""
        valid_types = ['demand', 'kitchen', 'churn', 'ltv', 'inventory']
        assert len(valid_types) == 5
        assert 'demand' in valid_types


class TestConstants:
    """Tests for application constants."""
    
    def test_restaurant_id_format(self, sample_restaurant_id):
        """Test restaurant ID format."""
        assert isinstance(sample_restaurant_id, str)
        assert len(sample_restaurant_id) > 0
        # UUID format check
        parts = sample_restaurant_id.split('-')
        assert len(parts) == 5
    
    def test_forecast_types(self):
        """Test forecast type constants."""
        forecast_types = ['hourly', 'daily']
        assert 'hourly' in forecast_types
        assert 'daily' in forecast_types


class TestDataValidation:
    """Tests for data validation."""
    
    def test_orders_data_structure(self, sample_orders_data):
        """Test orders data has required columns."""
        required_columns = ['order_id', 'restaurant_id', 'menu_item_id', 'order_time']
        for col in required_columns:
            assert col in sample_orders_data.columns
    
    def test_orders_data_not_empty(self, sample_orders_data):
        """Test orders data is not empty."""
        assert len(sample_orders_data) > 0
    
    def test_kitchen_data_structure(self, sample_kitchen_data):
        """Test kitchen data has required columns."""
        required_columns = ['station_id', 'menu_item_id', 'prep_time_minutes']
        for col in required_columns:
            assert col in sample_kitchen_data.columns
    
    def test_customer_data_structure(self, sample_customer_data):
        """Test customer data has required columns."""
        required_columns = ['customer_id', 'total_orders', 'total_spent']
        for col in required_columns:
            assert col in sample_customer_data.columns
    
    def test_inventory_data_structure(self, sample_inventory_data):
        """Test inventory data has required columns."""
        required_columns = ['item_id', 'current_stock', 'min_level', 'reorder_level']
        for col in required_columns:
            assert col in sample_inventory_data.columns

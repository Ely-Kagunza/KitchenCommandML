"""
Pytest configuration and fixtures.
"""

import pytest
import os
from datetime import datetime
import pandas as pd


@pytest.fixture
def sample_restaurant_id():
    """Sample restaurant ID for testing."""
    return "a33877ad-36ac-420a-96d0-6f518e5af21b"


@pytest.fixture
def sample_orders_data():
    """Sample orders data for testing."""
    return pd.DataFrame({
        'order_id': [1, 2, 3, 4, 5],
        'restaurant_id': ['a33877ad-36ac-420a-96d0-6f518e5af21b'] * 5,
        'menu_item_id': [1, 2, 1, 3, 2],
        'item_name': ['Burger', 'Fries', 'Burger', 'Pizza', 'Fries'],
        'category_name': ['Burgers', 'Sides', 'Burgers', 'Pizzas', 'Sides'],
        'order_time': pd.date_range(start='2024-01-01', periods=5, freq='h'),
        'quantity': [2, 1, 1, 3, 2],
        'total_amount': [20.0, 5.0, 10.0, 30.0, 5.0]
    })


@pytest.fixture
def sample_kitchen_data():
    """Sample kitchen performance data for testing."""
    return pd.DataFrame({
        'station_id': [1, 2, 1, 2, 1],
        'menu_item_id': [1, 2, 3, 1, 2],
        'prep_time_minutes': [5.5, 3.2, 8.1, 5.0, 3.5],
        'timestamp': pd.date_range(start='2024-01-01', periods=5, freq='h')
    })


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing."""
    return pd.DataFrame({
        'customer_id': [1, 2, 3, 4, 5],
        'total_orders': [10, 5, 20, 3, 15],
        'total_spent': [200.0, 50.0, 400.0, 30.0, 300.0],
        'avg_order_value': [20.0, 10.0, 20.0, 10.0, 20.0],
        'days_since_last_order': [5, 30, 2, 60, 10],
        'order_frequency': [2.0, 0.5, 5.0, 0.2, 3.0]
    })


@pytest.fixture
def sample_inventory_data():
    """Sample inventory data for testing."""
    return pd.DataFrame({
        'item_id': [1, 2, 3, 4, 5],
        'item_name': ['Tomatoes', 'Lettuce', 'Cheese', 'Beef', 'Buns'],
        'current_stock': [50, 30, 20, 15, 100],
        'min_level': [20, 15, 10, 10, 50],
        'reorder_level': [30, 20, 15, 15, 70],
        'daily_consumption_rate': [10, 5, 3, 4, 15]
    })


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv('DATABASE_URL', 'postgresql://test:test@localhost:5432/test_db')
    monkeypatch.setenv('MODEL_PATH', './models')
    monkeypatch.setenv('LOG_LEVEL', 'DEBUG')

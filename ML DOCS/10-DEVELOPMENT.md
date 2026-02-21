# Development Guide

## Overview

This guide covers setting up a development environment, coding standards, testing, and contributing to the ML service.

## Development Environment Setup

### Prerequisites

- Python 3.9+
- Git
- PostgreSQL client
- Redis
- Docker (optional)
- IDE (VS Code, PyCharm recommended)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/yourorg/ml-service.git
cd ml-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run tests
pytest

# Start development server
uvicorn src.api.app:app --reload
```

### IDE Configuration

**VS Code** (`.vscode/settings.json`):

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "100"],
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

**PyCharm**:

- Enable Black formatter
- Configure pytest as test runner
- Enable type checking
- Set line length to 100

## Project Structure

```
ml-service/
├── src/
│   ├── api/                    # FastAPI application
│   │   ├── app.py             # Main application
│   │   ├── routes/            # API routes
│   │   ├── auth.py            # Authentication
│   │   └── middleware.py      # Middleware
│   ├── models/                # ML model definitions
│   │   ├── demand.py
│   │   ├── kitchen.py
│   │   └── customer.py
│   ├── pipelines/             # Data pipelines
│   │   ├── data_extractor.py
│   │   ├── data_processor.py
│   │   └── feature_engineering.py
│   ├── training/              # Training scripts
│   │   ├── demand_trainer.py
│   │   ├── kitchen_trainer.py
│   │   └── customer_trainer.py
│   ├── services/              # Business logic
│   │   ├── prediction_service.py
│   │   └── model_loader.py
│   └── utils/                 # Utilities
│       ├── logging.py
│       ├── cache.py
│       └── metrics.py
├── tests/                     # Test suite
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── scripts/                   # Utility scripts
├── notebooks/                 # Jupyter notebooks
├── models/                    # Trained models
├── config/                    # Configuration files
├── docker/                    # Docker files
├── docs/                      # Documentation
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
├── pytest.ini                 # Pytest configuration
├── .pre-commit-config.yaml   # Pre-commit hooks
└── README.md
```

## Coding Standards

### Python Style Guide

Follow [PEP 8](https://pep8.org/) with these additions:

- Line length: 100 characters
- Use Black for formatting
- Use type hints
- Write docstrings for all public functions/classes

**Example**:

```python
from typing import List, Dict, Optional
import numpy as np

def calculate_demand_forecast(
    historical_data: np.ndarray,
    forecast_hours: int = 24,
    confidence_level: float = 0.95
) -> Dict[str, any]:
    """
    Calculate demand forecast for specified hours.

    Args:
        historical_data: Historical order data as numpy array
        forecast_hours: Number of hours to forecast (default: 24)
        confidence_level: Confidence level for intervals (default: 0.95)

    Returns:
        Dictionary containing:
            - predictions: List of predicted values
            - confidence_intervals: Upper and lower bounds
            - metadata: Additional information

    Raises:
        ValueError: If historical_data is empty or invalid

    Example:
        >>> data = np.array([10, 12, 15, 20])
        >>> forecast = calculate_demand_forecast(data, forecast_hours=12)
        >>> print(forecast['predictions'])
    """
    if len(historical_data) == 0:
        raise ValueError("Historical data cannot be empty")

    # Implementation
    predictions = []
    # ... logic here

    return {
        'predictions': predictions,
        'confidence_intervals': {'lower': [], 'upper': []},
        'metadata': {'model_version': '1.0.0'}
    }
```

### Code Organization

**Imports**:

```python
# Standard library imports
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Third-party imports
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

# Local imports
from src.pipelines.data_extractor import RMSDataExtractor
from src.utils.logging import setup_logging
```

**Class Structure**:

```python
class DemandForecaster:
    """Forecast demand for restaurant orders."""

    # Class constants
    DEFAULT_FORECAST_HOURS = 24
    MIN_TRAINING_SAMPLES = 1000

    def __init__(self, model_path: str):
        """Initialize forecaster with model path."""
        self.model_path = model_path
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load model from disk (private method)."""
        # Implementation
        pass

    def predict(self, features: np.ndarray) -> np.ndarray:
        """Make predictions (public method)."""
        # Implementation
        pass

    @staticmethod
    def validate_features(features: np.ndarray) -> bool:
        """Validate feature array (static method)."""
        # Implementation
        pass

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded (property)."""
        return self.model is not None
```

## Testing

### Test Structure

```
tests/
├── unit/                      # Unit tests
│   ├── test_data_extractor.py
│   ├── test_data_processor.py
│   ├── test_feature_engineering.py
│   └── test_models.py
├── integration/               # Integration tests
│   ├── test_api.py
│   ├── test_training_pipeline.py
│   └── test_prediction_service.py
├── fixtures/                  # Test fixtures
│   ├── sample_data.py
│   └── mock_models.py
└── conftest.py               # Pytest configuration
```

### Unit Tests

**Example** (`tests/unit/test_data_processor.py`):

```python
import pytest
import pandas as pd
import numpy as np
from src.pipelines.data_processor import DataProcessor

class TestDataProcessor:
    """Test DataProcessor class."""

    @pytest.fixture
    def processor(self):
        """Create DataProcessor instance."""
        return DataProcessor()

    @pytest.fixture
    def sample_orders(self):
        """Create sample order data."""
        return pd.DataFrame({
            'id': [1, 2, 3],
            'restaurant_id': [1, 1, 1],
            'grand_total': [50.0, 75.0, 100.0],
            'created_at': pd.date_range('2026-01-01', periods=3, freq='H')
        })

    def test_process_orders_success(self, processor, sample_orders):
        """Test successful order processing."""
        result = processor.process_orders(sample_orders)

        assert len(result) == 3
        assert 'is_weekend' in result.columns
        assert 'is_peak_hour' in result.columns

    def test_process_orders_removes_invalid(self, processor):
        """Test that invalid orders are removed."""
        invalid_orders = pd.DataFrame({
            'id': [1, 2],
            'restaurant_id': [1, 1],
            'grand_total': [-10.0, 50.0],  # Negative total
            'created_at': pd.date_range('2026-01-01', periods=2, freq='H')
        })

        result = processor.process_orders(invalid_orders)

        assert len(result) == 1  # Only valid order remains
        assert result.iloc[0]['grand_total'] == 50.0

    def test_process_orders_handles_missing_values(self, processor):
        """Test handling of missing values."""
        orders_with_nulls = pd.DataFrame({
            'id': [1, 2],
            'restaurant_id': [1, 1],
            'grand_total': [50.0, None],
            'created_at': pd.date_range('2026-01-01', periods=2, freq='H')
        })

        result = processor.process_orders(orders_with_nulls)

        # Should handle or remove null values
        assert result['grand_total'].notna().all()
```

### Integration Tests

**Example** (`tests/integration/test_api.py`):

```python
import pytest
from fastapi.testclient import TestClient
from src.api.app import app

class TestDemandForecastAPI:
    """Test demand forecast API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self):
        """Create authentication headers."""
        return {'Authorization': 'Bearer test_api_key'}

    def test_get_demand_forecast_success(self, client, auth_headers):
        """Test successful demand forecast request."""
        response = client.get(
            '/api/predictions/demand',
            params={'restaurant_id': 1, 'hours': 24},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert 'success' in data
        assert data['success'] is True
        assert 'data' in data
        assert 'predictions' in data['data']

    def test_get_demand_forecast_missing_params(self, client, auth_headers):
        """Test request with missing parameters."""
        response = client.get(
            '/api/predictions/demand',
            headers=auth_headers
        )

        assert response.status_code == 400

    def test_get_demand_forecast_unauthorized(self, client):
        """Test request without authentication."""
        response = client.get(
            '/api/predictions/demand',
            params={'restaurant_id': 1, 'hours': 24}
        )

        assert response.status_code == 401
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_data_processor.py

# Run specific test
pytest tests/unit/test_data_processor.py::TestDataProcessor::test_process_orders_success

# Run with verbose output
pytest -v

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

### Test Configuration

**File**: `pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --tb=short
    --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
```

## Pre-commit Hooks

**File**: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.9
        args: ['--line-length', '100']

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length', '100', '--ignore', 'E203,W503']

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ['--profile', 'black']

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## Debugging

### Local Debugging

**VS Code** (`.vscode/launch.json`):

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "src.api.app:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": false
    },
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    },
    {
      "name": "Python: Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-v", "${file}"],
      "console": "integratedTerminal"
    }
  ]
}
```

### Logging for Debugging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Use in code
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.exception("Exception with traceback")
```

## Performance Profiling

### Code Profiling

```python
import cProfile
import pstats

def profile_function():
    """Profile a function."""
    profiler = cProfile.Profile()
    profiler.enable()

    # Code to profile
    result = expensive_function()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions

    return result
```

### Memory Profiling

```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    """Profile memory usage."""
    large_list = [i for i in range(1000000)]
    return sum(large_list)
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def train_model(X: np.ndarray, y: np.ndarray, params: Dict) -> object:
    """
    Train machine learning model.

    This function trains a model using the provided data and parameters.
    It performs cross-validation and returns the best model.

    Args:
        X: Feature matrix of shape (n_samples, n_features)
        y: Target vector of shape (n_samples,)
        params: Dictionary of model hyperparameters
            - n_estimators: Number of trees (default: 100)
            - max_depth: Maximum tree depth (default: 6)

    Returns:
        Trained model object with fit() and predict() methods

    Raises:
        ValueError: If X and y have incompatible shapes
        TypeError: If params is not a dictionary

    Example:
        >>> X = np.array([[1, 2], [3, 4]])
        >>> y = np.array([0, 1])
        >>> params = {'n_estimators': 100}
        >>> model = train_model(X, y, params)

    Note:
        This function may take several minutes for large datasets.
    """
    pass
```

### Generating Documentation

```bash
# Install Sphinx
pip install sphinx sphinx-rtd-theme

# Initialize Sphinx
cd docs
sphinx-quickstart

# Generate API documentation
sphinx-apidoc -o source/ ../src/

# Build HTML documentation
make html
```

## Contributing

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/demand-forecasting-v2

# Make changes and commit
git add .
git commit -m "feat: improve demand forecasting accuracy"

# Push to remote
git push origin feature/demand-forecasting-v2

# Create pull request on GitHub
```

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:

```
feat(demand): add Prophet model for long-term forecasting

Implemented Prophet model to improve accuracy for weekly and monthly
forecasts. XGBoost is still used for hourly predictions.

Closes #123
```

```
fix(api): handle missing restaurant_id parameter

Added validation to return 400 error when restaurant_id is missing
instead of 500 internal server error.
```

### Pull Request Template

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally
```

## Useful Commands

```bash
# Format code
black src/ tests/

# Check code style
flake8 src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/

# Run linters
pylint src/

# Security check
bandit -r src/

# Dependency check
safety check

# Update dependencies
pip-compile requirements.in
pip-compile requirements-dev.in
```

---

**End of Documentation**

For questions or issues, please contact the ML team or create an issue on GitHub.

"""
Customer Lifetime Value (LTV) prediction model using Random Forest Regressor.
Predicts 12-month revenue per customer.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class CustomerLTVModel:
    """
    Random Forest model for predicting customer lifetime value.

    Predicts total revenue in next 12 months.
    """

    def __init__(self):
        """Initialize LTV prediction model."""
        self.logger = logging.getLogger(__name__)

        # Random Forest model
        self.model = RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1
        )

        # Feature scaler
        self.scaler = StandardScaler()

        # Label encoder for categorical features
        self.label_encoders = {}

        # Metadata
        self.feature_names = None
        self.categorical_features = []
        self.is_trained = False

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: np.ndarray,
        categorical_features: list = None
    ) -> Dict:
        """
        Train LTV prediction model.

        Args:
            X_train: Feature matrix
            y_train: Target values (12-month revenue)
            categorical_features: List of categorical feature names

        Returns:
            Dictionary with training metrics
        """
        self.logger.info("Training LTV prediction model...")

        # Store feature names
        if isinstance(X_train, pd.DataFrame):
            self.feature_names = X_train.columns.tolist()
            X_train = X_train.copy()
        else:
            self.feature_names = [f"feature_{i}" for i in range(X_train.shape[1])]
            X_train = pd.DataFrame(X_train, columns=self.feature_names)

        # Handle categorical features
        self.categorical_features = categorical_features or []
        for cat_feature in self.categorical_features:
            if cat_feature in X_train.columns:
                le = LabelEncoder()
                X_train[cat_feature] = le.fit_transform(X_train[cat_feature].astype(str))
                self.label_encoders[cat_feature] = le

        # Scale features
        X_scaled = self.scaler.fit_transform(X_train)

        # Train model
        self.model.fit(X_scaled, y_train)

        self.is_trained = True
        self.logger.info("LTV prediction model training complete!")

        return {'status': 'trained', 'n_estimators': self.model.n_estimators}

    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        """
        Predict customer LTV.

        Args:
            X_test: Feature matrix

        Returns:
            Array of predicted LTV values (non-negative)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained first")

        X_test = X_test.copy()

        # Encode categorical features
        for cat_feature in self.categorical_features:
            if cat_feature in X_test.columns and cat_feature in self.label_encoders:
                le = self.label_encoders[cat_feature]
                X_test[cat_feature] = le.transform(X_test[cat_feature].astype(str))

        X_scaled = self.scaler.transform(X_test)
        predictions = self.model.predict(X_scaled)

        # Ensure non-negative predictions
        return np.maximum(predictions, 0)

    def get_ltv_segments(self, X_test: pd.DataFrame) -> list:
        """
        Segment customers by predicted LTV.

        Args:
            X_test: Feature matrix

        Returns:
            List of LTV segments ('low_value', 'medium_value', 'high_value')
        """
        ltv = self.predict(X_test)

        # Define segments based on percentiles
        p33 = np.percentile(ltv, 33)
        p67 = np.percentile(ltv, 67)

        segments = []
        for value in ltv:
            if value < p33:
                segments.append('low_value')
            elif value < p67:
                segments.append('medium_value')
            else:
                segments.append('high_value')

        return segments

    def evaluate(
        self,
        X_test: pd.DataFrame,
        y_test: np.ndarray
    ) -> Dict:
        """
        Evaluate model performance.

        Args:
            X_test: Feature matrix
            y_test: True values

        Returns:
            Dictionary with evaluation metrics
        """
        predictions = self.predict(X_test)

        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        r2 = r2_score(y_test, predictions)

        # MAE as percentage of mean
        mae_pct = (mae / np.mean(y_test)) * 100 if np.mean(y_test) > 0 else 0

        metrics = {
            'mae': round(mae, 2),
            'rmse': round(rmse, 2),
            'r2': round(r2, 4),
            'mae_percentage': round(mae_pct, 2)
        }

        self.logger.info(f"Model evaluation: {metrics}")
        return metrics

    def get_feature_importance(self) -> Dict:
        """
        Get feature importance from Random Forest.

        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.is_trained:
            raise ValueError("Model must be trained first")

        importance = self.model.feature_importances_
        feature_importance = dict(zip(self.feature_names, importance))

        # Sort by importance
        return dict(sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        ))
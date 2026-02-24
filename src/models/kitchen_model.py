"""
Kitchen performance model using LightGMB.
Predicts preparation time for menu items at specific stations.
"""

import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class KitchenPerformanceModel:
    """
    LightGMB model for predicting kitchen prep times.

    Predicts how long it takes to prepare an item at a specific station.
    """

    def __init__(self):
        """Initialize kitchen performance model."""
        self.logger = logging.getLogger(__name__)

        # LightGBM model
        self.model = LGBMRegressor(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.05,
            num_leaves=31,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
            verbosity=-1
        )

        # Feature scaler
        self.scaler = StandardScaler()

        # Metadata
        self.feature_names = None
        self.is_trained = False

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: np.ndarray
    ) -> Dict:
        """
        Train kitchen performance model.

        Args:
            X_train: Feature matrix (n_samples, n_features)
            y_train: Target values (prep time in minutes)

        Returns:
            Dictionary with training metrics
        """
        self.logger.info("Training kitchen performance model...")

        # Store feature names
        if isinstance(X_train, pd.DataFrame):
            self.feature_names = X_train.columns.tolist()
        else:
            self.feature_names = [f"feature_{i}" for i in range(X_train.shape[1])]

        # Scale features
        X_scaled = self.scaler.fit_transform(X_train)

        # Train model
        self.model.fit(X_scaled, y_train)

        self.is_trained = True
        self.logger.info("Kitchen performance model training complete!")

        return {'status': 'trained', 'n_estimators': self.model.n_estimators}

    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        """
        Predict prep times.

        Args:
            X_text: Feature matrix

        Returns:
            Array of predicted prep times (minutes)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained first")

        X_scaled = self.scaler.transform(X_test)
        predictions = self.model.predict(X_scaled)

        # Ensure non-negative predictions
        return np.maximum(predictions, 0)

    def predict_with_confidence(self, X_test: pd.DataFrame) -> Dict:
        """
        Predict with confidence intervals.

        Args:
            X_test: Feature matrix

        Returns:
            Dictionary with predictions and bounds
        """
        predictions = self.predict(X_test)

        # Estimate std dev from residuals
        std_pred = np.std(predictions) * 0.2 # Conservative estimate

        return {
            'predictions': predictions,
            'lower_bound': np.maximum(predictions - 1.96 * std_pred, 0),
            'upper_bound': predictions + 1.96 * std_pred
        }

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

        # Within 5 minutes accuracy
        within_5 = np.mean(np.abs(y_test - predictions) <= 5) * 100

        metrics = {
            'mae': round(mae, 2),
            'rmse': round(rmse, 2),
            'r2': round(r2, 4),
            'within_5_minutes': round(within_5, 2)
        }

        self.logger.info(f"Model evaluation: {metrics}")
        return metrics

    def get_feature_importance(self) -> Dict:
        """
        Get feature importance from LightGBM.

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
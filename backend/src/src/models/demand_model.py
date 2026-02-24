"""
Demand forecasting model using XGBoost + Prophet ensemble.
Predicts order volume by hour/day/week.
"""

import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from prophet import Prophet
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from typing import Dict, Tuple, Optional
import logging
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class DemandForecastModel:
    """
    Ensemble model combining XGBoost and Prophet for demand forecasting.

    XGBoost: Short-term patterns (hours/days)
    Prophet: Long-term trends and seasonality (weeks/months)
    """

    def __init__(self, ensemble_weight: float = 0.7):
        """
        Initialize demand forcast model.

        Args:
            ensemble_weight: Weight for XGBoost (0-1). Prophet gets (1-weight)
                             Default: 0.7 (70% XGBoost, 30% Prophet)
        """
        self.ensemble_weight = ensemble_weight
        self.logger = logging.getLogger(__name__)

        # XGBoost model for short-term predictions
        self.xgb_model = XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
            verbosity=0
        )

        # Prophet model for long-term trends
        self.prophet_model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=True,
            changepoint_prior_scale=0.05,
            interval_width=0.95
        )

        # Feature scaler
        self.scaler = StandardScaler()

        # Metadata
        self.feature_names = None
        self.is_trained = False

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: np.ndarray,
        dates_train: pd.Series
    ) -> Dict:
        """
        Train both XGBoost and Prophet models.

        Args:
            X_train: Feature matrix (n_samples, n_features)
            y_train: Target values (order counts)
            dates_train: datetime series for Prophet

        Returns:
            Dictionary with training metrics
        """
        self.logger.info("Training demand forecast model...")

        # Store feature names
        if isinstance(X_train, pd.DataFrame):
            self.feature_names = X_train.columns.tolist()
        else:
            self.feature_names = [f"feature_{i}" for i in range(X_train.shape[1])]

        # Train XGBoost
        self.logger.info("Training XGBoost component...")
        X_scaled = self.scaler.fit_transform(X_train)
        self.xgb_model.fit(X_scaled, y_train)

        # Train Prophet (with fallback if it fails)
        self.logger.info("Training Prophet component...")
        try:
            prophet_df = pd.DataFrame({
                'ds': dates_train,
                'y': y_train
            })
            self.prophet_model.fit(prophet_df)
            self.logger.info("Prophet training successful")
        except Exception as e:
            self.logger.warning(f"Prophet training failed: {e}. Using XGBoost-only model.")
            self.prophet_model = None

        self.is_trained = True
        self.logger.info("Demand forecast model training complete!")

        return {'status': 'trained', 'xgb_trees': self.xgb_model.n_estimators}

    def predict(
        self,
        X_test: pd.DataFrame,
        dates_test: pd.Series
    ) -> np.ndarray:
        """
        Generate ensemble predictions.

        Args:
            X_test: Feature matrix for prediction
            dates_test: datetime series for Prophet

        Returns:
            Array of predicted order counts (non-negative)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        # XGBoost predictions
        X_scaled = self.scaler.transform(X_test)
        xgb_pred = self.xgb_model.predict(X_scaled)

        # If Prophet is available, use ensemble; otherwise use XGBoost only
        if self.prophet_model is not None:
            # Prophet predictions
            prophet_df = pd.DataFrame({'ds': dates_test})
            prophet_forecast = self.prophet_model.predict(prophet_df)
            prophet_pred = prophet_forecast['yhat'].values

            # Ensemble: weighted average
            ensemble_pred = (
                self.ensemble_weight * xgb_pred +
                (1 - self.ensemble_weight) * prophet_pred
            )
        else:
            # Use XGBoost only
            ensemble_pred = xgb_pred

        # Ensure non-negative predictions
        ensemble_pred = np.maximum(ensemble_pred, 0)

        return ensemble_pred

    def predict_with_confidence(
        self,
        X_test: pd.DataFrame,
        dates_test: pd.Series
    ) -> Dict:
        """
        Generate predictions with confidence intervals.

        Args:
            X_test: Feature matrix
            dates_test: datetime series

        Returns:
            Dictionary with predictions and bounds
        """
        predictions = self.predict(X_test, dates_test)

        if self.prophet_model is not None:
            # Calculate confidence intervals from Prophet
            prophet_df = pd.DataFrame({'ds': dates_test})
            prophet_forecast = self.prophet_model.predict(prophet_df)
            lower_bound = np.maximum(prophet_forecast['yhat_lower'].values, 0)
            upper_bound = prophet_forecast['yhat_upper'].values
        else:
            # Use predictions +/- 20% as bounds
            lower_bound = np.maximum(predictions * 0.8, 0)
            upper_bound = predictions * 1.2

        return {
            'predictions': predictions,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound
        }

    def evaluate(
        self,
        X_test: pd.DataFrame,
        y_test: np.ndarray,
        dates_test: pd.Series
    ) -> Dict:
        """
        Evaluate model performance.

        Args:
            X_test: Feature matrix
            y_test: True values
            dates_test: datetime series

        Returns:
            Dictionary with evaluation metrics
        """
        predictions = self.predict(X_test, dates_test)

        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        r2 = r2_score(y_test, predictions)
        mape = np.mean(np.abs((y_test - predictions) / (y_test + 1))) * 100

        # Within 5 orders accuracy
        within_5 = np.mean(np.abs(y_test - predictions) <= 5) * 100

        metrics = {
            'mae': round(mae, 2),
            'rmse': round(rmse, 2),
            'r2': round(r2, 4),
            'mape': round(mape, 2),
            'within_5_orders': round(within_5, 2)
        }

        self.logger.info(f"Model evaluation: {metrics}")
        return metrics

    def get_feature_importance(self) -> Dict:
        """
        Get XGBoost feature importance.

        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.is_trained:
            raise ValueError("Model must be trained first")

        importance = self.xgb_model.feature_importances_
        feature_importance = dict(zip(self.feature_names, importance))

        # Sort by importance
        return dict(sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        ))

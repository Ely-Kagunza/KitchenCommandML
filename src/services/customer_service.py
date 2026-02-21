"""
Customer analytics prediction service.
Predicts churn and lifetime value.
"""

import numpy as np
import pandas as pd
from typing import List, Dict
import logging
import joblib
import os

from src.pipelines.feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)


class CustomerPredictionService:
    """
    Service for customer analytics predictions.

    Predicts churn probability and lifetime value.
    """

    def __init__(self, churn_model_path: str, ltv_model_path: str):
        """
        Initialize customer prediction service.

        Args:
            churn_model_path: Path to churn prediction model
            ltv_model_path: Path to trained LTV model
        """
        self.logger = logging.getLogger(__name__)
        self.churn_model_path = churn_model_path
        self.ltv_model_path = ltv_model_path
        self.churn_model = None
        self.ltv_model = None
        self.feature_engineer = FeatureEngineer()

        self._load_models()

    def _load_models(self):
        """Load trained models from disk."""
        try:
            churn_file = os.path.join(self.churn_model_path, 'model.joblib')
            self.churn_model = joblib.load(churn_file)
            self.logger.info(f"Loaded churn model from {churn_file}")

            ltv_file = os.path.join(self.ltv_model_path, 'model.joblib')
            self.ltv_model = joblib.load(ltv_file)
            self.logger.info(f"Loaded LTV model from {ltv_file}")
        except Exception as e:
            self.logger.error(f"Error loading models: {e}")
            raise

    def predict_churn(
        self,
        customer_row: pd.Series
    ) -> Dict:
        """
        Predict customer churn probability.

        Args:
            customer_row: Customer data row

        Returns:
            Dictionary with churn prediction
        """
        # Create features
        features = self.feature_engineer.create_customer_features(customer_row)

        # Predict
        X = pd.DataFrame([features])
        churn_proba = self.churn_model.predict_proba(X)[0]
        risk_segment = self.churn_model.get_risk_segments(X)[0]

        return {
            'customer_id': int(customer_row['customer_id']),
            'churn_probability': round(churn_proba, 4),
            'risk_segment': risk_segment,
            'will_churn': int(churn_proba >= 0.5),
            'confidence': 0.85
        }

    def predict_ltv(
        self,
        customer_row: pd.Series
    ) -> Dict:
        """
        Predict customer lifetime value.

        Args:
            customer_row: Customer data row

        Returns:
            Dictionary with LTV prediction
        """
        # Create features
        features = self.feature_engineer.create_customer_features(customer_row)

        # Predict
        X = pd.DataFrame([features])
        ltv_pred = self.ltv_model.predict(X)[0]
        ltv_segment = self.ltv_model.get_ltv_segments(X)[0]

        return {
            'customer_id': int(customer_row['customer_id']),
            'predicted_ltv': round(ltv_pred, 2),
            'ltv_segment': ltv_segment,
            'confidence': 0.80
        }

    def predict_customer_analytics(
        self,
        customer_row: pd.Series
    ) -> Dict:
        """
        Get complete customer analytics.

        Args:
            customer_row: Customer data row

        Returns:
            Dictionary with churn and LTV predictions
        """
        churn_pred = self.predict_churn(customer_row)
        ltv_pred = self.predict_ltv(customer_row)

        return {
            'customer_id': int(customer_row['customer_id']),
            'churn': churn_pred,
            'ltv': ltv_pred,
            'recommendations': self._get_recommendations(churn_pred, ltv_pred),
            'generated_at': pd.Timestamp.now().isoformat()
        }

    def predict_batch_analytics(
        self,
        customer_df: pd.DataFrame
    ) -> Dict:
        """
        Predict analytics for a batch of customers.

        Args:
            customer_df: DataFrame of customer data

        Returns:
            Dictionary with batch predictions
        """
        predictions = []

        for idx, row in customer_df.iterrows():
            pred = self.predict_customer_analytics(row)
            predictions.append(pred)

        return {
            'batch_size': len(customer_df),
            'predictions': predictions,
            'generated_at': pd.Timestamp.now().isoformat()
        }

    def get_at_risk_customers(
        self,
        customer_df: pd.DataFrame,
        churn_threshold: float = 0.6
    ) -> Dict:
        """
        Identify customers at risk of churn.

        Args:
            customer_df: DataFrame of customer data
            churn_threshold: Churn probability threshold

        Returns:
            Dictionary with at-risk customers
        """
        at_risk = []

        for idx, row in customer_df.iterrows():
            churn_pred = self.predict_churn(row)

            if churn_pred['churn_probability'] >= churn_threshold:
                at_risk.append({
                    'customer_id': churn_pred['customer_id'],
                    'churn_probability': churn_pred['churn_probability'],
                    'risk_segment': churn_pred['risk_segment'],
                    'current_points': int(row['current_points']),
                    'days_since_last_order': int(row['recency_days'])
                })

        # Sort by churn probability
        at_risk.sort(key=lambda x: x['churn_probability'], reverse=True)

        return {
            'analysis_type': 'at_risk_customers',
            'threshold': churn_threshold,
            'at_risk_count': len(at_risk),
            'customers': at_risk,
            'generated_at': pd.Timestamp.now().isoformat()
        }

    def get_high_value_customers(
        self,
        customer_df: pd.DataFrame,
        ltv_percentile: float = 75
    ) -> Dict:
        """
        Identify high-value customers.

        Args:
            customer_df: DataFrame of customer data
            ltv_percentile: Percentile threshold for high value

        Returns:
            Dictionary with high-value customers
        """
        ltv_predictions = []

        for idx, row in customer_df.iterrows():
            ltv_pred = self.predict_ltv(row)
            ltv_predictions.append(ltv_pred['predicted_ltv'])

        threshold = np.percentile(ltv_predictions, ltv_percentile)

        high_value = []

        for idx, row in customer_df.iterrows():
            ltv_pred = self.predict_ltv(row)

            if ltv_pred['predicted_ltv'] >= threshold:
                high_value.append({
                    'customer_id': ltv_pred['customer_id'],
                    'predicted_ltv': ltv_pred['predicted_ltv'],
                    'ltv_segment': ltv_pred['ltv_segment'],
                    'total_spent': row['total_spent'],
                    'total_orders': int(row['total_orders'])
                })

        # Sort by predicted LTV
        high_value.sort(key=lambda x: x['predicted_ltv'], reverse=True)

        return {
            'analysis_type': 'high_value_customers',
            'percentile_threshold': ltv_percentile,
            'ltv_threshold': round(threshold, 2),
            'high_value_count': len(high_value),
            'customers': high_value,
            'generated_at': pd.Timestamp.now().isoformat()
        }

    def _get_recommendations(
        self,
        churn_pred: Dict,
        ltv_pred: Dict
    ) -> List[str]:
        """
        Get recommendations based on predictions.

        Args:
            churn_pred: Churn prediction dictionary
            ltv_pred: LTV prediction dictionary

        Returns:
            List of recommendations
        """
        recommendations = []

        # Churn-based recommendations
        if churn_pred['churn_probability'] >= 0.7:
            recommendations.append("Send personalized retention offer")
            recommendations.append("Offer loyalty points bonus")
        elif churn_pred['churn_probability'] >= 0.5:
            recommendations.append("Send engagement email")

        # LTV-based recommendations
        if ltv_pred['ltv_segment'] == 'high_value':
            recommendations.append("VIP treatment - priority service")
            recommendations.append("Exclusive menu items access")
        elif ltv_pred['ltv_segment'] == 'medium_value':
            recommendations.append("Encourage repeat visits")

        return recommendations
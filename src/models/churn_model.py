"""
Customer churn prediction model using XGBoost Classifier.
Predicts probability of customer churn.
"""

import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report
)
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class CustomerChurnModel:
    """
    XGBoost classifier for predicting customer churn.

    Churn defined as: No order in last 60 days
    """

    def __init__(self, threshold: float = 0.5):
        """
        Initialize churn prediction model.

        Args:
            threshold: Probability threshold for churn classification (0-1)
        """
        self.logger = logging.getLogger(__name__)
        self.threshold = threshold

        # XGBoost classifier with class weight for imbalance
        self.model = XGBClassifier(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.1,
            scale_pos_weight=3, # Handle class imbalance
            random_state=42,
            n_jobs=-1,
            verbosity=0
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
        y_train: pd.ndarray,
        categorical_features: list = None
    ) -> Dict:
        """
        Train churn prediction model.

        Args:
            X_train: Feature matrix
            y_train: Target values (0=active, 1=churned)
            categorical_features: List of categorical feature names

        Returns:
            Dictionary with training metrics
        """
        self.logger.info("Training churn prediction model...")

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
        self.logger.info("Churn prediction model training complete!")

        return {'status': 'trained', 'n_estimators': self.model.n_estimators}

    def predict_proba(self, X_test: pd.DataFrame) -> np.ndarray:
        """
        Predict churn probability.

        Args:
            X_test: Feature matrix

        Returns:
            Array of churn probabilities (0-1)
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
        return self.model.predict_proba(X_scaled)[:, 1]

    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        """
        Predict churn classification.

        Args:
            X_test: Feature matrix

        Returns:
            Array of predictions (0=active, 1=churned)
        """
        proba = self.predict_proba(X_test)
        return (proba >= self.threshold).astype(int)

    def get_risk_segments(self, X_test: pd.DataFrame) -> list:
        """
        Segment customers by churn risk.

        Args:
            X_test: Feature matrix

        Returns:
            List of risk segments ('low_risk', 'medium_risk', 'high_risk')
        """
        proba = self.predict_proba(X_test)

        segments = []
        for p in proba:
            if p < 0.3:
                segments.append('low_risk')
            elif p < 0.6:
                segments.append('medium_risk')
            else:
                segments.append('high_risk')

        return segments

    def evaluate(
        self,
        X_test: pd.DataFrame,
        y_test: pd.ndarray
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
        proba = self.predict_proba(X_test)

        precision = precision_score(y_test, predictions)
        recall = recall_score(y_test, predictions)
        f1 = f1_score(y_test, predictions)
        auc_roc = roc_auc_score(y_test, proba)

        metrics = {
            'precision': round(precision, 4),
            'recall': round(recall, 4),
            'f1': round(f1, 4),
            'auc_roc': round(auc_roc, 4)
        }

        self.logger.info(f"Model evaluation: {metrics}")
        return metrics

    def get_feature_importance(self) -> Dict:
        """
        Get feature importance.

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
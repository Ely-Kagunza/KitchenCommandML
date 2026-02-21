"""
Model loader utility for managing trained models.
"""

import os
import json
import logging
from typing import Dict, Optional
from datetime import datetime
import joblib

logger = logging.getLogger(__name__)


class ModelLoader:
    """
    Utility for loading and managing trained models.
    """

    def __init__(self, model_base_dir: str = "models"):
        """
        Initialize model loader.

        Args:
            model_base_dir: Base directory for models
        """
        self.logger = logging.getLogger(__name__)
        self.model_base_dir = model_base_dir
        self.loaded_models = {}

    def get_latest_model_path(
        self,
        model_type: str,
        restaurant_id: int
    ) -> Optional[str]:
        """
        Get path to latest model version.

        Args:
            model_type: Model type (demand, kitchen, churn, ltv, inventory)
            restaurant_id: Restaurant ID

        Returns:
            Path to latest model or None if not found
        """
        model_dir = os.path.join(
            self.model_base_dir,
            model_type,
            f"restaurant_{restaurant_id}"
        )

        latest_link = os.path.join(model_dir, "latest")

        if os.path.exists(latest_link):
            return latest_link

        return None

    def load_model(
        self,
        model_type: str,
        restaurant_id: int
    ):
        """
        Load model from disk

        Args:
            model_type: Type of model
            restaurant_id: Restaurant ID

        Returns:
            Loaded model or None if not found
        """
        model_path = self.get_latest_model_path(model_type, restaurant_id)

        if not model_path:
            self.logger.warning(f"Model not found: {model_type} for restaurant {restaurant_id}")
            return None

        try:
            model_file = os.path.join(model_path, "model.joblib")
            model = joblib.load(model_file)
            self.logger.info(f"Loaded {model_type} model from {model_file}")
            return model
        except Exception as e:
            self.logger.error(f"Error loading {model_type} model: {str(e)}")
            return None

    def get_model_metadata(
        self,
        model_type: str,
        restaurant_id: int
    ) -> Optional[Dict]:
        """
        Get model metadata.

        Args:
            model_type: Type of model
            restaurant_id: Restaurant ID

        Returns:
            Metadata disctionary or None
        """
        model_path = self.get_latest_model_path(model_type, restaurant_id)

        if not model_path:
            return None
        
        try:
            metadata_file = os.path.join(model_path, "metadata.json")
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
            return metadata
        except Exception as e:
            self.logger.error(f"Error loading metadata: {str(e)}")
            return None

    def list_model_versions(
        self,
        model_type: str,
        restaurant_id: int
    ) -> list:
        """
        List all versions of a model.

        Args:
            model_type: Type of model
            restaurant_id: Restaurant ID

        Returns:
          List of version directories
        """
        model_dir = os.path.join(
            self.model_base_dir,
            model_type,
            f"restaurant_{restaurant_id}"
        )

        if not os.path.exists(model_dir):
            return []

        versions = [
            d for d in os.listdir(model_dir)
            if os.path.isdir(os.path.join(model_dir, d)) and d != "latest"
        ]

        return sorted(versions, reverse=True)

    def get_model_info(
        self,
        model_type: str,
        restaurant_id: int
    ) -> Dict:
        """
        Get comprehensive model information.

        Args:
            model_type: Type of model
            restaurant_id: Restaurant ID

        Returns:
            Dictionary with model information
        """
        metadata = self.get_model_metadata(model_type, restaurant_id)
        versions = self.list_model_versions(model_type, restaurant_id)

        return {
            'model_type': model_type,
            'restaurant_id': restaurant_id,
            'latest_metadata': metadata,
            'all_versions': versions,
            'version_count': len(versions)
        }
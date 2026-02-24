"""
Script to train all ML models.
"""

import os
import sys
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from config.logging import setup_logging
from src.training.train_pipeline import ModelTrainingPipeline

# Setup logging
logger = setup_logging()


def main():
    """Train all models."""
    logger.info("=" * 80)
    logger.info("Starting Model Training Pipeline")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 80)

    try:
        # Initialize pipeline
        pipeline = ModelTrainingPipeline(
            db_url=settings.DATABASE_URL,
            model_dir=settings.MODEL_BASE_DIR,
            restaurant_id=1  # Can be parameterized
        )

        # Train all models
        results = pipeline.train_all_models()

        # Log results
        logger.info("=" * 80)
        logger.info("Training Complete")
        logger.info(f"Summary: {results['summary']}")
        logger.info("=" * 80)

        # Print detailed results
        for model_type, result in results['models'].items():
            logger.info(f"\n{model_type.upper()}:")
            logger.info(f"  Status: {result['status']}")
            if result['status'] == 'success':
                logger.info(f"  Metrics: {result.get('metrics', {})}")
                logger.info(f"  Samples: {result.get('samples', 'N/A')}")
            else:
                logger.error(f"  Error: {result.get('error', 'Unknown')}")

        # Close pipeline
        pipeline.close()

        return 0

    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

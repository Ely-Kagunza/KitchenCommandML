"""
Test script to train models and identify issues.
"""

import os
import sys
import logging
from config.settings import settings
from config.logging import setup_logging

# Setup logging
logger = setup_logging()

# Validate settings
try:
    settings.validate()
    logger.info("Settings validated successfully")
except ValueError as e:
    logger.error(f"Settings validation failed: {e}")
    sys.exit(1)

from src.training.train_pipeline import ModelTrainingPipeline

# Initialize pipeline
db_url = os.getenv('DATABASE_URL')
if not db_url:
    logger.error("DATABASE_URL not set")
    sys.exit(1)

restaurant_id = "a33877ad-36ac-420a-96d0-6f518e5af21b"  # Use actual UUID from your database

pipeline = ModelTrainingPipeline(db_url, restaurant_id=restaurant_id)

try:
    print("\n" + "="*50)
    print("Training demand model...")
    print("="*50)
    pipeline.train_demand_model()
    print("[OK] Demand model trained successfully")
except Exception as e:
    print(f"[ERROR] Error training demand model: {str(e)}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    print("\n")

try:
    print("\n" + "="*50)
    print("Training kitchen model...")
    print("="*50)
    pipeline.train_kitchen_model()
    print("[OK] Kitchen model trained successfully")
except Exception as e:
    print(f"[ERROR] Error training kitchen model: {str(e)}")
    import traceback
    traceback.print_exc()

try:
    print("\n" + "="*50)
    print("Training churn model...")
    print("="*50)
    pipeline.train_churn_model()
    print("[OK] Churn model trained successfully")
except Exception as e:
    print(f"[ERROR] Error training churn model: {str(e)}")
    import traceback
    traceback.print_exc()

try:
    print("\n" + "="*50)
    print("Training LTV model...")
    print("="*50)
    pipeline.train_ltv_model()
    print("[OK] LTV model trained successfully")
except Exception as e:
    print(f"[ERROR] Error training LTV model: {str(e)}")
    import traceback
    traceback.print_exc()

try:
    print("\n" + "="*50)
    print("Training inventory model...")
    print("="*50)
    pipeline.train_inventory_model()
    print("[OK] Inventory model trained successfully")
except Exception as e:
    print(f"[ERROR] Error training inventory model: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("Training complete!")
print("="*50)

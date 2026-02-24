"""
Analyze kitchen model training results.
"""

import os
import sys
import json
from pathlib import Path
from config.settings import settings
from config.logging import setup_logging

logger = setup_logging()

try:
    settings.validate()
except ValueError as e:
    logger.error(f"Settings validation failed: {e}")
    sys.exit(1)

from src.training.train_pipeline import ModelTrainingPipeline
from src.utils.model_loader import ModelLoader

db_url = os.getenv('DATABASE_URL')
restaurant_id = "a33877ad-36ac-420a-96d0-6f518e5af21b"

pipeline = ModelTrainingPipeline(db_url, restaurant_id=restaurant_id)

print("\n" + "="*60)
print("KITCHEN MODEL TRAINING ANALYSIS")
print("="*60)

# Train kitchen model
result = pipeline.train_kitchen_model()

print("\nTraining Result:")
print(f"  Status: {result.get('status')}")
print(f"  Model Type: {result.get('model_type')}")
print(f"  Training Samples: {result.get('samples')}")

print("\nPerformance Metrics:")
metrics = result.get('metrics', {})
for key, value in metrics.items():
    print(f"  {key}: {value}")

# Load the model from disk to get feature importance
try:
    model_loader = ModelLoader('models')
    kitchen_model = model_loader.load_model('kitchen', restaurant_id)
    
    if kitchen_model and hasattr(kitchen_model, 'get_feature_importance'):
        print("\nFeature Importance (Top 10):")
        importance = kitchen_model.get_feature_importance()
        for i, (feature, score) in enumerate(list(importance.items())[:10], 1):
            print(f"  {i}. {feature}: {score:.4f}")
        
        print("\nAll Features:")
        for feature, score in importance.items():
            print(f"  - {feature}: {score:.4f}")
except Exception as e:
    print(f"\nNote: Could not load model for feature importance: {e}")

print("\n" + "="*60)

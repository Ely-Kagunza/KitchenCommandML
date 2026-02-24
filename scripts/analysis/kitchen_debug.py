"""
Debug kitchen model training data.
"""

import os
import sys
from config.settings import settings
from config.logging import setup_logging

logger = setup_logging()

try:
    settings.validate()
except ValueError as e:
    logger.error(f"Settings validation failed: {e}")
    sys.exit(1)

from src.pipelines.data_extractor import RMSDataExtractor
from src.pipelines.data_processor import DataProcessor, DataValidator
from src.pipelines.feature_engineering import FeatureEngineer
from datetime import datetime, timedelta

db_url = os.getenv('DATABASE_URL')
restaurant_id = "a33877ad-36ac-420a-96d0-6f518e5af21b"

extractor = RMSDataExtractor(db_url)
processor = DataProcessor()
validator = DataValidator()
feature_engineer = FeatureEngineer()

print("\n" + "="*60)
print("KITCHEN DATA DEBUG")
print("="*60)

# Extract kitchen data
end_date = datetime.now()
start_date = end_date - timedelta(days=90)

raw_data = extractor.extract_kitchen_performance(
    restaurant_id,
    start_date.strftime('%Y-%m-%d'),
    end_date.strftime('%Y-%m-%d')
)

print(f"\nRaw kitchen data shape: {raw_data.shape}")
print(f"Columns: {raw_data.columns.tolist()}")
print(f"\nFirst few rows:")
print(raw_data.head())

# Validate
validation = validator.validate_kitchen_data(raw_data)
print(f"\nValidation: {validation}")

# Process
kitchen_data = processor.process_kitchen_data(raw_data)
print(f"\nProcessed kitchen data shape: {kitchen_data.shape}")
print(f"Columns: {kitchen_data.columns.tolist()}")
print(f"\nFirst few rows:")
print(kitchen_data.head())

# Check unique stations and items
print(f"\nUnique stations: {kitchen_data['station_id'].nunique()}")
print(f"Unique items: {kitchen_data['menu_item_id'].nunique()}")
print(f"Prep time stats:")
print(kitchen_data['prep_time_minutes'].describe())

# Create features for a sample
print(f"\nSample features:")
for idx in range(min(3, len(kitchen_data))):
    row = kitchen_data.iloc[idx]
    features = feature_engineer.create_kitchen_features(
        kitchen_data,
        row['station_id'],
        row['menu_item_id']
    )
    print(f"\nRow {idx}:")
    print(f"  Station: {row['station_id']}, Item: {row['menu_item_id']}, Prep Time: {row['prep_time_minutes']}")
    for key, value in features.items():
        print(f"  {key}: {value}")

print("\n" + "="*60)

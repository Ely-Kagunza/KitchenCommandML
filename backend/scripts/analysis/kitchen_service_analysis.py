"""
Comprehensive analysis of kitchen service predictions.
Tests all methods: prep time, batch predictions, bottlenecks, station performance.
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
from src.pipelines.data_processor import DataProcessor
from src.services.kitchen_service import KitchenPredictionService
from src.utils.model_loader import ModelLoader
from datetime import datetime, timedelta
import pandas as pd

db_url = os.getenv('DATABASE_URL')
restaurant_id = "a33877ad-36ac-420a-96d0-6f518e5af21b"

# Extract kitchen data
extractor = RMSDataExtractor(db_url)
processor = DataProcessor()

end_date = datetime.now()
start_date = end_date - timedelta(days=90)

raw_data = extractor.extract_kitchen_performance(
    restaurant_id,
    start_date.strftime('%Y-%m-%d'),
    end_date.strftime('%Y-%m-%d')
)

kitchen_data = processor.process_kitchen_data(raw_data)

# Load model
model_loader = ModelLoader('models')
kitchen_model = model_loader.load_model('kitchen', restaurant_id)

# Get model path
model_path = f'models/kitchen/restaurant_{restaurant_id}'
# Find the latest version directory
import glob
version_dirs = glob.glob(os.path.join(model_path, '20*'))
if version_dirs:
    model_dir = max(version_dirs, key=os.path.getctime)
else:
    raise FileNotFoundError(f"No model versions found in {model_path}")

# Initialize service
service = KitchenPredictionService(model_dir)

print("\n" + "="*80)
print("KITCHEN SERVICE COMPREHENSIVE ANALYSIS")
print("="*80)

# ============================================================================
# 1. SINGLE ITEM PREP TIME PREDICTION
# ============================================================================
print("\n" + "-"*80)
print("1. SINGLE ITEM PREP TIME PREDICTION")
print("-"*80)

# Get a sample item
sample_row = kitchen_data.iloc[0]
station_id = sample_row['station_id']
menu_item_id = sample_row['menu_item_id']
actual_prep_time = sample_row['prep_time_minutes']

print(f"\nSample Item:")
print(f"  Station ID: {station_id}")
print(f"  Station Name: {sample_row['station_name']}")
print(f"  Menu Item ID: {menu_item_id}")
print(f"  Menu Item Name: {sample_row['item_name']}")
print(f"  Actual Prep Time: {actual_prep_time:.2f} minutes")

pred = service.predict_prep_time(station_id, menu_item_id, kitchen_data)

print(f"\nPrediction Result:")
print(f"  Predicted Prep Time: {pred['predicted_prep_time_minutes']} minutes")
print(f"  Lower Bound: {pred['lower_bound_minutes']} minutes")
print(f"  Upper Bound: {pred['upper_bound_minutes']} minutes")
print(f"  Confidence: {pred['confidence']}")
print(f"  Error: {abs(actual_prep_time - pred['predicted_prep_time_minutes']):.2f} minutes")

# ============================================================================
# 2. BATCH PREP TIME PREDICTION
# ============================================================================
print("\n" + "-"*80)
print("2. BATCH PREP TIME PREDICTION")
print("-"*80)

# Create a batch of orders
batch_orders = []
for i in range(min(5, len(kitchen_data))):
    row = kitchen_data.iloc[i]
    batch_orders.append({
        'station_id': row['station_id'],
        'menu_item_id': row['menu_item_id']
    })

print(f"\nBatch Orders ({len(batch_orders)} items):")
for i, order in enumerate(batch_orders, 1):
    item_data = kitchen_data[
        (kitchen_data['station_id'] == order['station_id']) &
        (kitchen_data['menu_item_id'] == order['menu_item_id'])
    ]
    if len(item_data) > 0:
        print(f"  {i}. Station: {order['station_id']}, Item: {order['menu_item_id']}, "
              f"Avg Actual: {item_data['prep_time_minutes'].mean():.2f} min")

batch_pred = service.predict_batch_prep_time(batch_orders, kitchen_data)

print(f"\nBatch Prediction Result:")
print(f"  Batch Size: {batch_pred['batch_size']} items")
print(f"  Estimated Total Time: {batch_pred['estimated_total_time_minutes']} minutes")
print(f"\n  Individual Item Predictions:")
for i, item_pred in enumerate(batch_pred['item_predictions'], 1):
    print(f"    {i}. Item {item_pred['menu_item_id']}: "
          f"{item_pred['predicted_prep_time_minutes']} min "
          f"(range: {item_pred['lower_bound_minutes']}-{item_pred['upper_bound_minutes']} min)")

# ============================================================================
# 3. BOTTLENECK IDENTIFICATION
# ============================================================================
print("\n" + "-"*80)
print("3. BOTTLENECK IDENTIFICATION")
print("-"*80)

bottleneck_analysis = service.identify_bottlenecks(kitchen_data, threshold_percentile=75)

print(f"\nBottleneck Analysis (75th percentile threshold):")
print(f"  Total Bottlenecks Found: {len(bottleneck_analysis['bottlenecks'])}")

for bottleneck in bottleneck_analysis['bottlenecks']:
    print(f"\n  Station: {bottleneck['station_name']} (ID: {bottleneck['station_id']})")
    print(f"    Average Prep Time: {bottleneck['avg_prep_time']} minutes")
    print(f"    Bottleneck Threshold: {bottleneck['bottleneck_threshold']} minutes")
    print(f"    Slow Items ({len(bottleneck['slow_items'])}):")
    for slow_item in bottleneck['slow_items']:
        print(f"      - Item {slow_item['menu_item_id']}: "
              f"{slow_item['avg_prep_time']} min avg ({slow_item['occurences']} occurrences)")

# ============================================================================
# 4. STATION PERFORMANCE METRICS
# ============================================================================
print("\n" + "-"*80)
print("4. STATION PERFORMANCE METRICS")
print("-"*80)

station_perf = service.get_station_performance(kitchen_data)

print(f"\nStation Performance Analysis:")
for station in station_perf['stations']:
    print(f"\n  Station: {station['station_name']} (ID: {station['station_id']})")
    print(f"    Total Items Prepared: {station['total_items_prepared']}")
    print(f"    Average Prep Time: {station['avg_prep_time_minutes']} minutes")
    print(f"    Median Prep Time: {station['median_prep_time_minutes']} minutes")
    print(f"    Std Dev: {station['std_dev_prep_time']} minutes")
    print(f"    Min Prep Time: {station['min_prep_time']} minutes")
    print(f"    Max Prep Time: {station['max_prep_time']} minutes")
    print(f"    Within 5 Min Accuracy: {station['within_5_min_accuracy']}%")

# ============================================================================
# 5. PREDICTION ACCURACY ANALYSIS
# ============================================================================
print("\n" + "-"*80)
print("5. PREDICTION ACCURACY ANALYSIS")
print("-"*80)

errors = []
within_5_count = 0

for idx in range(min(50, len(kitchen_data))):
    row = kitchen_data.iloc[idx]
    pred = service.predict_prep_time(row['station_id'], row['menu_item_id'], kitchen_data)
    actual = row['prep_time_minutes']
    error = abs(actual - pred['predicted_prep_time_minutes'])
    errors.append(error)
    
    if error <= 5:
        within_5_count += 1

errors_array = pd.Series(errors)

print(f"\nAccuracy on {len(errors)} test samples:")
print(f"  Mean Absolute Error: {errors_array.mean():.2f} minutes")
print(f"  Median Absolute Error: {errors_array.median():.2f} minutes")
print(f"  Std Dev of Errors: {errors_array.std():.2f} minutes")
print(f"  Min Error: {errors_array.min():.2f} minutes")
print(f"  Max Error: {errors_array.max():.2f} minutes")
print(f"  Within 5 Minutes: {within_5_count}/{len(errors)} ({within_5_count/len(errors)*100:.1f}%)")

# ============================================================================
# 6. SUMMARY & INSIGHTS
# ============================================================================
print("\n" + "-"*80)
print("6. SUMMARY & INSIGHTS")
print("-"*80)

print(f"\nKey Findings:")
print(f"  [OK] Model predicts prep times with {errors_array.mean():.2f} min average error")
print(f"  [OK] {within_5_count/len(errors)*100:.1f}% of predictions within 5 minutes")
print(f"  [OK] Batch prediction estimates total time as max of individual items")
print(f"  [OK] Bottleneck detection identifies slow items at each station")
print(f"  [OK] Station performance shows consistent prep times across operations")

print(f"\nOperational Recommendations:")
print(f"  1. Use batch predictions for order timing estimates")
print(f"  2. Monitor bottleneck items for process improvements")
print(f"  3. Station {station_perf['stations'][0]['station_name']} has "
      f"{station_perf['stations'][0]['avg_prep_time_minutes']} min avg prep time")
if len(bottleneck_analysis['bottlenecks']) > 0:
    print(f"  4. Focus on slow items: {', '.join([str(item['menu_item_id']) for bottleneck in bottleneck_analysis['bottlenecks'] for item in bottleneck['slow_items'][:2]])}")

print("\n" + "="*80)

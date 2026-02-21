"""
Inventory optimization prediction service.
Provides stock recommendations and optimization.
"""

import numpy as np
import pandas as pd
from typing import Dict, List
import logging
import joblib
import os

from src.pipelines.feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)


class InventoryPredictionService:
    """
    Service for inventory optimization predictions.
    
    Recommends reorder points, quantities, and stock levels.
    """

    def __init__(self, model_path: str):
        """
        Initialize inventory prediction service.

        Args:
            model_path: Path to trained model directory
        """
        self.logger = logging.getLogger(__name__)
        self.model_path = model_path
        self.model = None
        self.feature_engineer = FeatureEngineer()

        self._load_model()

    def _load_model(self):
        """Load trained model from disk."""
        try:
            model_file = os.path.join(self.model_path, 'model.joblib')
            self.model = joblib.load(model_file)
            self.logger.info(f"Loaded inventory model from {model_file}")
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            raise

    def predict_reorder_point(
        self,
        daily_consumption_rate: float,
        lead_time_days: int,
        consumption_std_dev: float
    ) -> Dict:
        """
        Predict optimal reorder point.

        Args:
            daily_consumption_rate: Average daily consumption
            lead_time_days: Supplier lead time
            consumption_std_dev: Standard deviation of consumption

        Returns:
            Dictionary with reorder point
        """
        result = self.model.predict_reorder_point(
            daily_consumption_rate,
            lead_time_days,
            consumption_std_dev
        )

        return {
            'reorder_point': round(result['reorder_point'], 1),
            'safety_stock': round(result['safety_stock'], 1),
            'avg_demand_during_lead_time': round(result['avg_demand_during_lead_time'], 1),
            'service_level': result['service_level']
        }

    def predict_order_quantity(
        self,
        annual_demand: float,
        order_cost: float,
        holding_cost: float
    ) -> Dict:
        """
        Predict optimal order quantity (EOQ).

        Args:
            annual_demand: Total annual demand
            order_cost: Cost per order
            holding_cost: Annual holding cost per unit

        Returns:
            Dictionary with optimal order quantity
        """
        result = self.model.predict_order_quantity(
            annual_demand,
            order_cost,
            holding_cost
        )

        return {
            'optimal_order_quantity': round(result['optimal_order_quantity'], 1),
            'orders_per_year': round(result['orders_per_year'], 1),
            'average_inventory': round(result['average_inventory'], 1),
            'total_cost': round(result['total_cost'], 2)
        }

    def predict_stock_forecast(
        self,
        current_stock: float,
        daily_consumption_rate: float,
        days_ahead: int = 30
    ) -> Dict:
        """
        Forecast stock levels.

        Args:
            current_stock: Current stock level
            daily_consumption_rate: Daily consumption
            days_ahead: Days to forecast

        Returns:
            Dictionary with stock forecast
        """
        result = self.model.predict_stock_forecast(
            current_stock,
            daily_consumption_rate,
            days_ahead
        )

        return {
            'projected_stock': round(result['projected_stock_in_30_days'], 1),
            'days_until_stockout': round(result['days_until_stockout'], 1),
            'will_stockout': result['will_stockout'],
            'stock_status': result['stock_status']
        }

    def get_item_recommendation(
        self,
        item_id: int,
        current_stock: float,
        daily_consumption_rate: float,
        reorder_point: float,
        optimal_order_qty: float,
        min_level: float = 0,
        max_level: float = None
    ) -> Dict:
        """
        Get inventory recommendation for item.

        Args:
            item_id: Item ID
            current_stock: Current stock
            daily_consumption_rate: Daily consumption
            reorder_point: Reorder point
            optimal_order_qty: Optimal order quantity
            min_level: Minimum stock level
            max_level: Maximum stock level

        Returns:
            Dictionary with recommendation
        """
        recommendation = self.model.get_recommendations(
            current_stock,
            reorder_point,
            optimal_order_qty,
            daily_consumption_rate,
            min_level,
            max_level
        )

        return {
            'item_id': item_id,
            'current_stock': current_stock,
            'action': recommendation['action'],
            'urgency': recommendation['urgency'],
            'reason': recommendation['reason'],
            'recommended_order_qty': recommendation['recommended_order_qty'],
            'generated_at': pd.Timestamp.now().isoformat()
        }

    def get_batch_recommendations(
        self,
        inventory_df: pd.DataFrame
    ) -> Dict:
        """
        Get recommendations for batch of items.

        Args:
            inventory_df: DataFrame with inventory data

        Returns:
            Dictionary with batch recommendations
        """
        recommendations = []

        for idx, row in inventory_df.iterrows():
            rec = self.get_item_recommendation(
                item_id=int(row['item_id']),
                current_stock=row['current_stock'],
                daily_consumption_rate=row['daily_consumption_rate'],
                reorder_point=row['reorder_level'],
                optimal_order_qty=row['reorder_level'] * 2,
                min_level=row['min_level']
            )
            recommendations.append(rec)

        # Sort by urgency
        urgency_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        recommendations.sort(
            key=lambda x: urgency_order.get(x['urgency'], 4)
        )

        return {
            'batch_size': len(inventory_df),
            'recommendations': recommendations,
            'critical_count': sum(1 for r in recommendations if r['urgency'] == 'critical'),
            'high_count': sum(1 for r in recommendations if r['urgency'] == 'high'),
            'generated_at': pd.Timestamp.now().isoformat()
        }

    def get_reorder_summary(
        self,
        inventory_df: pd.DataFrame
    ) -> Dict:
        """
        Get summary of items needing reorder.

        Args:
            inventory_df: DataFrame with inventory data

        Returns:
            Dictionary with reorder summary
        """
        recommendations = self.get_batch_recommendations(inventory_df)

        # Filter for reorder actions
        reorder_items = [
            r for r in recommendations['recommendations']
            if r['action'] in ['reorder', 'emergency_reorder']
        ]

        total_reorder_qty = sum(r['recommended_order_qty'] for r in reorder_items)

        return {
            'summary_type': 'reorder_summary',
            'items_needing_reorder': len(reorder_items),
            'total_reorder_quantity': round(total_reorder_qty, 1),
            'items': reorder_items,
            'generated_at': pd.Timestamp.now().isoformat()
        }

    def get_stock_status_report(
        self,
        inventory_df: pd.DataFrame
    ) -> Dict:
        """
        Get overall stock status report.

        Args:
            inventory_df: DataFrame with inventory data

        Returns:
            Dictionary with stock status report
        """
        status_counts = {
            'healthy': 0,
            'medium': 0,
            'low': 0,
            'critical': 0
        }

        status_details = {
            'healthy': [],
            'medium': [],
            'low': [],
            'critical': []
        }

        for idx, row in inventory_df.iterrows():
            forecast = self.predict_stock_forecast(
                row['current_stock'],
                row['daily_consumption_rate'],
                days_ahead=30
            )

            status = forecast['stock_status']
            status_counts[status] += 1

            status_details[status].append({
                'item_id': int(row['item_id']),
                'item_name': row['item_name'],
                'current_stock': row['current_stock'],
                'projected_stock': forecast['projected_stock'],
                'days_until_stockout': forecast['days_until_stockout']
            })

        return {
            'report_type': 'stock_status',
            'total_items': len(inventory_df),
            'status_summary': status_counts,
            'status_details': status_details,
            'generated_at': pd.Timestamp.now().isoformat()
        }

    def optimize_inventory(
        self,
        item_id: int,
        current_stock: float,
        daily_consumption_rate: float,
        lead_time_days: int,
        order_cost: float,
        holding_cost: float,
        min_level: float = 0,
        max_level: float = None
    ) -> Dict:
        """
        Comprehensive inventory optimization for item.

        Args:
            item_id: Item ID
            current_stock: Current stock level
            daily_consumption_rate: Daily consumption
            lead_time_days: Supplier lead time
            order_cost: Cost per order
            holding_cost: Annual holding cost per unit
            min_level: Minimum stock level
            max_level: Maximum stock level

        Returns:
            Dictionary with optimization results
        """
        # Calculate annual demand
        annual_demand = daily_consumption_rate * 365

        # Estimate consumption std dev (assume 20% of mean)
        consumption_std_dev = daily_consumption_rate * 0.2

        # Get reorder point
        reorder_result = self.predict_reorder_point(
            daily_consumption_rate,
            lead_time_days,
            consumption_std_dev
        )

        # Get order quantity
        eoq_result = self.predict_order_quantity(
            annual_demand,
            order_cost,
            holding_cost
        )

        # Get stock forecast
        forecast = self.predict_stock_forecast(
            current_stock,
            daily_consumption_rate,
            days_ahead=30
        )

        # Get recommendation
        recommendation = self.get_item_recommendation(
            item_id,
            current_stock,
            daily_consumption_rate,
            reorder_result['reorder_point'],
            eoq_result['optimal_order_quantity'],
            min_level,
            max_level
        )

        return {
            'item_id': item_id,
            'optimization': {
                'reorder_point': reorder_result['reorder_point'],
                'safety_stock': reorder_result['safety_stock'],
                'optimal_order_quantity': eoq_result['optimal_order_quantity'],
                'orders_per_year': eoq_result['orders_per_year'],
                'annual_holding_cost': eoq_result['total_cost']
            },
            'current_status': {
                'current_stock': current_stock,
                'daily_consumption': daily_consumption_rate,
                'annual_demand': annual_demand
            },
            'forecast': forecast,
            'recommendation': recommendation,
            'generated_at': pd.Timestamp.now().isoformat()
        }

    def get_waste_reduction_insights(
        self,
        inventory_df: pd.DataFrame
    ) -> Dict:
        """
        Get insights for waste reduction.

        Args:
            inventory_df: DataFrame with inventory data

        Returns:
            Dictionary with waste reduction insights
        """
        insights = []

        for idx, row in inventory_df.iterrows():
            # Check for items with high stock and low consumption
            if row['current_stock'] > row['reorder_level'] * 3:
                days_supply = row['current_stock'] / max(row['daily_consumption_rate'], 0.1)

                if days_supply > 60:
                    insights.append({
                        'item_id': int(row['item_id']),
                        'item_name': row['item_name'],
                        'issue': 'Excess inventory',
                        'current_stock': row['current_stock'],
                        'days_supply': round(days_supply, 1),
                        'recommendation': 'Reduce order quantity or frequency',
                        'potential_savings': round(
                            (row['current_stock'] - row['reorder_level']) * row['avg_unit_cost'],
                            2
                        )
                    })

            # Check for items with expiry soon
            if row['earliest_expiry'] is not None:
                days_to_expiry = (row['earliest_expiry'] - pd.Timestamp.now()).days

                if 0 < days_to_expiry <= 7:
                    insights.append({
                        'item_id': int(row['item_id']),
                        'item_name': row['item_name'],
                        'issue': 'Expiry risk',
                        'current_stock': row['current_stock'],
                        'days_to_expiry': days_to_expiry,
                        'recommendation': 'Prioritize usage or promote item',
                        'potential_loss': round(
                            row['current_stock'] * row['avg_unit_cost'],
                            2
                        )
                    })

        return {
            'analysis_type': 'waste_reduction',
            'insights_count': len(insights),
            'insights': insights,
            'generated_at': pd.Timestamp.now().isoformat()
        }

    def get_cost_analysis(
        self,
        inventory_df: pd.DataFrame,
        order_cost: float,
        holding_cost_per_unit_per_day: float = 0.01
    ) -> Dict:
        """
        Get inventory cost analysis.

        Args:
            inventory_df: DataFrame with inventory data
            order_cost: Cost per order
            holding_cost_per_unit_per_day: Daily holding cost per unit

        Returns:
            Dictionary with cost analysis
        """
        total_holding_cost = 0
        total_ordering_cost = 0
        items_analysis = []

        for idx, row in inventory_df.iterrows():
            annual_demand = row['daily_consumption_rate'] * 365

            # Calculate costs
            eoq_result = self.predict_order_quantity(
                annual_demand,
                order_cost,
                holding_cost_per_unit_per_day * 365
            )

            holding_cost = eoq_result['average_inventory'] * holding_cost_per_unit_per_day * 365
            ordering_cost = eoq_result['orders_per_year'] * order_cost

            total_holding_cost += holding_cost
            total_ordering_cost += ordering_cost

            items_analysis.append({
                'item_id': int(row['item_id']),
                'item_name': row['item_name'],
                'annual_demand': annual_demand,
                'holding_cost': round(holding_cost, 2),
                'ordering_cost': round(ordering_cost, 2),
                'total_cost': round(holding_cost + ordering_cost, 2)
            })

        # Sort by total cost
        items_analysis.sort(key=lambda x: x['total_cost'], reverse=True)

        return {
            'analysis_type': 'cost_analysis',
            'total_items': len(inventory_df),
            'total_holding_cost': round(total_holding_cost, 2),
            'total_ordering_cost': round(total_ordering_cost, 2),
            'total_inventory_cost': round(total_holding_cost + total_ordering_cost, 2),
            'items': items_analysis,
            'generated_at': pd.Timestamp.now().isoformat()
        }

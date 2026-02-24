"""
Inventory optimization model using Time Series Forecasting and Optimization.
Predicts optimal stock levels and reorder points.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Dict, Tuple
import logging
from scipy.stats import norm

logger = logging.getLogger(__name__)


class InventoryOptimizationModel:
    """
    Inventory optimization model for predicting reorder points and quantities.

    Uses demand forecasting and cost optimization.
    """

    def __init__(
        self,
        holding_cost_per_unit_per_day: float = 0.01,
        stockout_cost_per_unit: float = 10.0,
        service_level: float = 0.95
    ):
        """
        Initialize inventory optimization model.

        Args:
            holding_cost_per_unit_per_day: Daily holding cost per unit
            stockout_cost_per_unit: Cost per unit of stockout
            service_level: Target service level (0-1)
        """
        self.logger = logging.getLogger(__name__)
        self.holding_cost_per_unit_per_day = holding_cost_per_unit_per_day
        self.stockout_cost_per_unit = stockout_cost_per_unit
        self.service_level = service_level

        # Z-score for service level
        self.z_score = self._get_z_score(service_level)

        self.is_trained = False

    def train(self, historical_data: pd.DataFrame) -> Dict:
        """
        Train inventory model on historical data.

        Args:
            historical_data: DataFrame with historical consumption data

        Returns:
            Dictionary with training metrics
        """
        self.logger.info("Training inventory optimization model...")

        # Validate input data
        if len(historical_data) < 30:
            raise ValueError("Need at least 30 days of historical data")

        self.is_trained = True
        self.logger.info("Inventory optimization model training complete!")

        return {'status': 'trained', 'data_points': len(historical_data)}

    def predict_reorder_point(
        self,
        daily_consumption_rate: float,
        lead_time_days: int,
        consumption_std_dev: float
    ) -> Dict:
        """
        Calculate optimal reorder point.

        Args:
            daily_consumption_rate: Average daily consumption rate
            lead_time_days: Supplier lead time in days
            consumption_std_dev: Standard deviation of daily consumption

        Returns:
            Dictionary with reorder point and safety stock
        """
        if not self.is_trained:
            raise ValueError("Model must be trained first")

        # Average demand during lead time
        avg_demand_during_lead_time = daily_consumption_rate * lead_time_days

        # Safety stock (z-score method)
        safety_stock = self.z_score * consumption_std_dev * np.sqrt(lead_time_days)

        # Reorder point
        reorder_point = avg_demand_during_lead_time + safety_stock

        return {
            'reorder_point': max(reorder_point, 0),
            'safety_stock': max(safety_stock, 0),
            'avg_demand_during_lead_time': avg_demand_during_lead_time,
            'service_level': self.service_level
        }

    def predict_order_quantity(
        self,
        annual_demand: float,
        order_cost: float,
        holding_cost: float
    ) -> Dict:
        """
        Calculate Economic Order Quantity (EOQ).

        Args:
            annual_demand: Total annual demand
            order_cost: Cost per order
            holding_cost: Annual holding cost per unit

        Returns:
            Dictionary with optimal order quantity and costs
        """
        if annual_demand <= 0 or order_cost <= 0 or holding_cost <= 0:
            return {
                'optimal_order_quantity': 0,
                'orders_per_year': 0,
                'total_cost': 0,
                'average_inventory': 0
            }

        # EOQ formula: sqrt((2 * D * S) / H)
        eoq = np.sqrt((2 * annual_demand * order_cost) / holding_cost)

        # Orders per year
        orders_per_year = annual_demand / eoq if eoq > 0 else 0

        # Average inventory
        average_inventory = eoq / 2

        # Total cost (holding + ordering)
        total_cost = (orders_per_year * order_cost) + (average_inventory * holding_cost)

        return {
            'optimal_order_quantity': max(eoq, 1),
            'orders_per_year': max(orders_per_year, 1),
            'average_inventory': average_inventory,
            'total_cost': total_cost
        }

    def predict_stock_forecast(
        self,
        current_stock: float,
        daily_consumption_rate: float,
        days_ahead: int = 30
    ) -> Dict:
        """
        Forecast stock levels for next N days.

        Args:
            current_stock: Current stock level
            daily_consumption_rate: Average daily consumption rate
            days_ahead: Number of days to forecast

        Returns:
            Dictionary with forecasted stock levels
        """
        # Project stock levels
        projected_stock = current_stock - (daily_consumption_rate * days_ahead)

        # Days until stockout
        if daily_consumption_rate > 0:
            days_until_stockout = current_stock / daily_consumption_rate
        else:
            days_until_stockout = np.inf

        # Stock status
        if projected_stock < 0:
            stock_status = 'critical'
        elif projected_stock < (daily_consumption_rate * 7):
            stock_status = 'low'
        elif projected_stock < (daily_consumption_rate * 14):
            stock_status = 'medium'
        else:
            stock_status = 'healthy'

        return {
            'projected_stock_in_30_days': max(projected_stock, 0),
            'days_until_stockout': days_until_stockout,
            'will_stockout': projected_stock < 0,
            'stock_status': stock_status
        }

    def get_recommendations(
        self,
        current_stock: float,
        reorder_point: float,
        optimal_order_qty: float,
        daily_consumption_rate: float,
        min_level: float = 0,
        max_level: float = None
    ) -> Dict:
        """
        Get inventory recommendations.

        Args:
            current_stock: Current stock level
            reorder_point: Calculated reorder point
            optimal_order_qty: Optimal order quantity
            daily_consumption_rate: Average daily consumption rate
            min_level: Minimum stock level
            max_level: Maximum stock level

        Returns:
            Dictionary with recommendations
        """
        recommendations = {
            'action': 'hold',
            'urgency': 'low',
            'reason': 'Stock level is healthy',
            'recommended_order_qty': 0,
        }

        # Check if reorder needed
        if current_stock <= reorder_point:
            recommendations['action'] = 'reorder'
            recommendations['order_quantity'] = optimal_order_qty
            recommendations['urgency'] = 'high'
            recommendations['reason'] = f'Stock below reorder point ({reorder_point:.0f})'

        # Check if stock is critically low
        if current_stock <= min_level:
            recommendations['action'] = 'emergency_reorder'
            recommendations['urgency'] = 'critical'
            recommendations['reason'] = f'Stock below minimum level ({min_level:.0f})'
            recommendations['recommended_order_qty'] = optimal_order_qty * 1.5

        # Check if stock is approaching max level
        if max_level and current_stock >= max_level:
            recommendations['action'] = 'reduce_orders'
            recommendations['urgency'] = 'medium'
            recommendations['reason'] = f'Stock above maximum level ({max_level:.0f})'
            recommendations['recommended_order_qty'] = 0

        return recommendations

    def calculate_safety_stock(
        self,
        consumption_std_dev: float,
        lead_time_days: int
    ) -> float:
        """
        Calculate safety stock.

        Args:
            consumption_std_dev: Standard deviation of daily consumption
            lead_time_days: Lead time in days

        Returns:
            Safety stock quantity
        """
        return self.z_score * consumption_std_dev * np.sqrt(lead_time_days)

    def calculate_holding_cost(
        self,
        average_inventory: float,
        unit_cost: float
    ) -> float:
        """
        Calculate annual holding cost.

        Args:
            average_inventory: Average inventory level
            unit_cost: Cost per unit

        Returns:
            Annual holding cost
        """
        return average_inventory * unit_cost * self.holding_cost_per_unit_per_day * 365

    def calculate_ordering_cost(
        self,
        annual_demand: float,
        order_quantity: float,
        cost_per_order: float
    ) -> float:
        """
        Calculate annual ordering cost.

        Args:
            annual_demand: Total annual demand
            order_quantity: Quantity per order
            cost_per_order: Cost per order

        Returns:
            Annual ordering cost
        """
        if order_quantity <= 0:
            return 0
        return (annual_demand / order_quantity) * cost_per_order

    def optimize_inventory(
        self,
        current_stock: float,
        reorder_point: float,
        daily_consumption_rate: float,
        lead_time_days: int,
        holding_cost: float,
        order_cost: float
    ) -> Dict:
        """
        Comprehensive inventory optimization.

        Args:
            current_stock: Current stock level
            reorder_point: Calculated reorder point
            daily_consumption_rate: Average daily consumption rate
            lead_time_days: Lead time in days
            holding_cost: Annual holding cost per unit per year
            order_cost: Cost per order

        Returns:
            Dictionary with optimization results
        """
        # Calculate annual demand
        annual_demand = daily_consumption_rate * 365

        # Calculate EOQ
        eoq_result = self.predict_order_quantity(
            annual_demand,
            order_cost,
            holding_cost
        )

        # calculate costs
        holding_cost_annual = self.calculate_holding_cost(
            eoq_result['average_inventory'],
            holding_cost
        )

        ordering_cost_annual = self.calculate_ordering_cost(
            annual_demand,
            eoq_result['optimal_order_quantity'],
            order_cost
        )

        # Stock forecast
        forecast = self.predict_stock_forecast(
            current_stock,
            daily_consumption_rate,
            days_ahead=30
        )

        # recommendations
        recommendations = self.get_recommendations(
            current_stock,
            reorder_point,
            eoq_result['optimal_order_quantity'],
            daily_consumption_rate
        )

        return {
            'eoq': eoq_result['optimal_order_quantity'],
            'reorder_point': reorder_point,
            'annual_demand': annual_demand,
            'holding_cost_annual': holding_cost_annual,
            'ordering_cost_annual': ordering_cost_annual,
            'total_cost_annual': holding_cost_annual + ordering_cost_annual,
            'forecast': forecast,
            'recommendations': recommendations
        }

    def _get_z_score(self, service_level: float) -> float:
        """
        Get z-score for given service level.

        Args:
            service_level: Service level (0-1)

        Returns:
            Z-score
        """
        # Convert service level to percentile
        percentile = service_level * 100

        # Get z-score from normal distribution table
        z_score = norm.ppf(percentile)

        return z_score

    def evaluate(
        self,
        actual_stockouts: int,
        total_periods: int,
        actual_holding_cost: float,
        predicted_holding_cost: float,
    ) -> Dict:
        """
        Evaluate model performance.

        Args:
            actual_stockouts: Number of stockout events
            total_periods: Total number of periods
            actual_holding_cost: Actual holding cost
            predicted_holding_cost: Predicted holding cost

        Returns:
            Dictionary with evaluation metrics
        """
        # Stockout rate
        actual_service_level = 1 - (actual_stockouts / total_periods)

        # Cost accuracy
        cost_error = abs(actual_holding_cost - predicted_holding_cost) / actual_holding_cost * 100

        metrics = {
            'actual_service_level': round(actual_service_level, 4),
            'target_service_level': self.service_level,
            'stockout_rate': round(actual_stockouts / total_periods * 100, 2),
            'cost_error_percentage': round(cost_error, 2),
        }

        self.logger.info(f"Model evaluation metrics: {metrics}")
        return metrics

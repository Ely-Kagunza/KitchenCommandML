"""
Data extraction module for RMS database
Connects to RMS PostgreSQL and extracts raw data for ML models.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import pandas as pd
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RMSDataExtractor:
    """Extract data from RMS PostgreSQL database (read-only)."""

    def __init__(self, db_url: str):
        """
        Initialize database connection.

        Args:
            db_url (str): PostgreSQL connection string
                postgresql://user:pass@host:port/dbname
        """
        self.engine = create_engine(
          db_url,
          poolclass=NullPool,
          connect_args={
            'options': '-c default_transaction_read_only=on'
          }
        )
        self.logger = logging.getLogger(__name__)

    def extract_orders(
      self,
      restauranr_id: int,
      start_date: str,
      end_date: str
    ) -> pd.DataFrame:
      """
      Extract order data for demand forcasting.

      Args:
          restaurant_id: Restaurant identifier
          start_date: Start date (YYYY-MM-DD)
          end_date: End date (YYYY-MM-DD)

      Returns:
          DataFrame with order details
      """
      query = """
      SELECT
          o.id,
          o.restaurant_id,
          o.service_type,
          o.grand_total,
          o.created_at,
          DATE_TRUNC('hour', o.created_at) as order_hour,
          EXTRACT(DOW FROM o.created_at) as day_of_week,
          EXTRACT(HOUR FROM o.created_at) as hour_of_day,
          oi.menu_item_id,
          mi.name as item_name,
          mc.name as category_name,
          oi.quantity,
          oi.unit_price
      FROM orders_order o
      JOIN orders_orderitem oi ON o.id = oi.order_id
      JOIN menus_menuitem mi ON oi.menu_item_id = mi.id
      JOIN menus_menucategory mc ON mi.category_id = mc.id
      WHERE o.restaurant_id = :restaurant_id
        AND o.status IN ('completed', 'paid')
        AND o.created_at >= :start_date
        AND o.created_at < :end_date
      ORDER BY o.created_at;
      """

      try:
          df = pd.read_sql(
              text(query),
              self.engine,
              params={
                  'restaurant_id': restauranr_id,
                  'start_date': start_date,
                  'end_date': end_date
              }
          )
          self.logger.info(f"Extracted {len(df)} order records")
          return df
      except Exception as e:
          self.logger.error(f"Error extracting orders: {e}")
          raise

    def extract_kitchen_performance(
        self,
        restaurant_id: int,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Extract kitchen timing data for prep time prediction.

        Args:
            restaurant_id: Restaurant identifier
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            DataFrame with kitchen performance data
        """
        query = """
        SELECT
            ois.id,
            ois.station_id,
            ks.name as station_name,
            oi.menu_item_id,
            mi.name as item_name,
            oi.quantity,
            ois.assigned_at,
            ois.started_at,
            ois.completed_at,
            EXTRACT(EPOCH FROM (ois.completed_at - ois.assigned_at))/60 as total_time_minutes,
            EXTRACT(EPOCH FROM (ois.completed_at - ois.started_at))/60 as prep_time_minutes,
            EXTRACT(EPOCH FROM (ois.started_at - ois.assigned_at))/60 as queue_time_minutes,
            EXTRACT(DOW FROM ois.assigned_at) as day_of_week,
            EXTRACT(HOUR FROM ois.assigned_at) as hour_of_day
        FROM kitchen_orderitemstation ois
        JOIN kitchen_kitchenstation ks ON ois.station_id = ks.id
        JOIN orders_orderitem oi ON ois.order_item_id = oi.id
        JOIN menus_menuitem mi ON oi.menu_item_id = mi.id
        WHERE ks.restaurant_id = :restaurant_id
          AND ois.status = 'completed'
          AND ois.completed_at IS NOT NULL
          AND ois.assigned_at >= :start_date
          AND ois.assigned_at < :end_date
        ORDER BY ois.assigned_at;
        """

        try:
            df = pd.read_sql(
                text(query),
                self.engine,
                params={
                    'restaurant_id': restaurant_id,
                    'start_date': start_date,
                    'end_date': end_date
                }
            )
            self.logger.info(f"Extracted {len(df)} kitchen performance records")
            return df
        except Exception as e:
            self.logger.error(f"Error extracting kitchen performance: {e}")
            raise

    def extract_customer_data(
        self,
        restaurant_id: int
    ) -> pd.DataFrame:
        """
        Extract customer profiles and behavior data.

        Args:
            restaurant_id: Restaurant identifier

        Returns:
            DataFrame with customer data
        """
        query = """
        SELECT
            cp.id as customer_id,
            cp.restaurant_id,
            cp.created_at as customer_since,
            EXTRACT(EPOCH FROM (NOW() - cp.created_at))/86400 as days_since_signup,
            COALESCE(lb.current_points, 0) as current_points,
            COALESCE(lb.lifetime_points, 0) as lifetime_points,
            COALESCE(lb.current_tier, 'bronze') as current_tier,
            COUNT(DISTINCT o.id) as total_orders,
            COALESCE(SUM(o.grand_total), 0) as total_spent,
            COALESCE(AVG(o.grand_total), 0) as avg_order_value,
            MAX(o.created_at) as last_order_date,
            EXTRACT(EPOCH FROM (NOW() - MAX(o.created_at)))/86400 as days_since_last_order,
            COUNT(DISTINCT DATE(o.created_at)) as unique_order_days
        FROM crm_customerprofile cp
        LEFT JOIN crm_loyaltybalance lb ON cp.id = lb.customer_id
        LEFT JOIN orders_order o ON cp.id = o.customer_id 
            AND o.status IN ('completed', 'paid')
        WHERE cp.restaurant_id = :restaurant_id
        GROUP BY cp.id, lb.current_points, lb.lifetime_points, lb.current_tier;
        """
        try:
            df = pd.read_sql(
                text(query),
                self.engine,
                params={
                    'restaurant_id': restaurant_id
                }
            )
            self.logger.info(f"Extracted {len(df)} customer records")
            return df
        except Exception as e:
            self.logger.error(f"Error extracting customer data: {e}")
            raise
        
    def extract_inventory_data(
        self,
        restaurant_id: int
    ) -> pd.DataFrame:
        """
        Extract inventory levels and consumption data.

        Args:
            restaurant_id: Restaurant identifier

        Returns:
            DataFrame with inventory data
        """
        query = """
        SELECT
            ii.id as item_id,
            ii.restaurant_id,
            ii.name as item_name,
            COALESCE(ic.name, 'Uncategorized') as category_name,
            ii.min_level,
            ii.reorder_level,
            COALESCE(SUM(b.remaining_base), 0) as current_stock,
            COUNT(b.id) as batch_count,
            MIN(b.expiry_date) as earliest_expiry,
            COALESCE(AVG(b.unit_cost_per_base), 0) as avg_unit_cost,
            COALESCE(
                (SELECT SUM(ABS(sm.qty_base))
                 FROM inventory_stockmovement sm
                 WHERE sm.item_id = ii.id
                   AND sm.movement_type = 'recipe_deduct'
                   AND sm.created_at >= NOW() - INTERVAL '30 days'),
                0
            ) as consumption_last_30_days
        FROM inventory_inventoryitem ii
        LEFT JOIN inventory_category ic ON ii.category_id = ic.id
        LEFT JOIN inventory_batch b ON ii.id = b.item_id 
            AND b.remaining_base > 0
        WHERE ii.restaurant_id = :restaurant_id
          AND ii.is_active = TRUE
        GROUP BY ii.id, ic.name;
        """

        try:
            df = pd.read_sql(
                text(query),
                self.engine,
                params={
                    'restaurant_id': restaurant_id
                }
            )
            self.logger.info(f"Extracted {len(df)} inventory records")
            return df
        except Exception as e:
            self.logger.error(f"Error extracting inventory data: {e}")
            raise

    def extract_payment_data(
        self,
        restaurant_id: int,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Extract payment data for analysis.

        Args:
            restaurant_id: Restaurant identifier
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            DataFrame with payment data
        """
        query = """
        SELECT
            p.id,
            p.order_id,
            p.restaurant_id,
            p.payment_method,
            p.amount,
            COALESCE(p.tip_amount, 0) as tip_amount,
            p.status,
            p.created_at,
            p.completed_at,
            EXTRACT(HOUR FROM p.created_at) as hour_of_day,
            EXTRACT(DOW FROM p.created_at) as day_of_week
        FROM payments_payment p
        WHERE p.restaurant_id = :restaurant_id
          AND p.created_at >= :start_date
          AND p.created_at < :end_date
        ORDER BY p.created_at;
        """

        try:
            df = pd.read_sql(
                text(query),
                self.engine,
                params={
                    'restaurant_id': restaurant_id,
                    'start_date': start_date,
                    'end_date': end_date
                }
            )
            self.logger.info(f"Extracted {len(df)} payment records")
            return df
        except Exception as e:
            self.logger.error(f"Error extracting payment data: {e}")
            raise

    def close(self):
        """Close database connection."""
        self.engine.dispose()
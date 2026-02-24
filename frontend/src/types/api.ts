import type { ApiResponse } from './common'

/**
 * Demand Forecasting API Types
 */
export interface DemandPrediction {
  timestamp: string
  hour?: number
  predicted_orders: number
  confidence: number
}

export interface DemandForecastRequest {
  restaurant_id: string
  forecast_type: 'hourly' | 'daily'
  hours_ahead?: number
  days_ahead?: number
}

export interface DemandForecastResponse extends ApiResponse<{
  forecast_type: 'hourly' | 'daily'
  hours_ahead?: number
  days_ahead?: number
  predictions: DemandPrediction[]
}> {}

export interface ItemDemandResponse extends ApiResponse<{
  item_id: number
  item_name: string
  forecast_type: string
  hours_ahead: number
  predictions: DemandPrediction[]
}> {}

export interface PeakHoursResponse extends ApiResponse<{
  analysis_type: string
  days_ahead: number
  analysis: Array<{
    date: string
    peak_hours: Array<{
      hour: number
      predicted_orders: number
    }>
  }>
}> {}

/**
 * Kitchen Service API Types
 */
export interface KitchenPredictionRequest {
  restaurant_id: string
  station_id: number
  menu_item_id: number
}

export interface PrepTimePrediction {
  station_id: number
  menu_item_id: number
  predicted_prep_time_minutes: number
  lower_bound_minutes: number
  upper_bound_minutes: number
  confidence: number
}

export interface PrepTimeResponse extends ApiResponse<PrepTimePrediction> {}

export interface BatchPrepTimeRequest {
  restaurant_id: string
  orders: Array<{
    station_id: number
    menu_item_id: number
  }>
}

export interface BatchPrepTimeResponse extends ApiResponse<{
  batch_size: number
  item_predictions: PrepTimePrediction[]
  estimated_total_time_minutes: number
  generated_at: string
}> {}

export interface BottleneckItem {
  menu_item_id: number
  avg_prep_time: number
  occurences: number
}

export interface BottleneckStation {
  station_id: string
  station_name: string
  avg_prep_time: number
  bottleneck_threshold: number
  slow_items: BottleneckItem[]
}

export interface BottlenecksResponse extends ApiResponse<{
  analysis_type: string
  bottlenecks: BottleneckStation[]
  generated_at: string
}> {}

export interface StationMetrics {
  station_id: string
  station_name: string
  total_items_prepared: number
  avg_prep_time_minutes: number
  median_prep_time_minutes: number
  std_dev_prep_time: number
  min_prep_time: number
  max_prep_time: number
  within_5_min_accuracy: number
}

export interface StationPerformanceResponse extends ApiResponse<{
  analysis_type: string
  stations: StationMetrics[]
  generated_at: string
}> {}

/**
 * Customer Analytics API Types
 */
export interface ChurnPrediction {
  customer_id: number
  churn_probability: number
  risk_segment: string
  will_churn: number
  confidence: number
}

export interface ChurnResponse extends ApiResponse<ChurnPrediction> {}

export interface LTVPrediction {
  customer_id: number
  predicted_ltv: number
  ltv_segment: string
  confidence: number
}

export interface LTVResponse extends ApiResponse<LTVPrediction> {}

export interface CustomerAnalytic {
  customer_id: number
  churn: ChurnPrediction
  ltv: LTVPrediction
  recommendations: string[]
}

export interface BatchAnalyticsResponse extends ApiResponse<{
  batch_size: number
  predictions: CustomerAnalytic[]
  generated_at: string
}> {}

export interface AtRiskCustomer {
  customer_id: number
  churn_probability: number
  risk_segment: string
  current_points: number
  days_since_last_order: number
}

export interface AtRiskCustomersResponse extends ApiResponse<{
  analysis_type: string
  threshold: number
  at_risk_count: number
  customers: AtRiskCustomer[]
  generated_at: string
}> {}

export interface HighValueCustomer {
  customer_id: number
  predicted_ltv: number
  ltv_segment: string
  total_spent: number
  total_orders: number
}

export interface HighValueCustomersResponse extends ApiResponse<{
  analysis_type: string
  percentile_threshold: number
  ltv_threshold: number
  high_value_count: number
  customers: HighValueCustomer[]
  generated_at: string
}> {}

/**
 * Inventory Management API Types
 */
export interface InventoryRecommendation {
  item_id: number
  current_stock: number
  action: 'maintain' | 'reorder' | 'emergency_reorder' | 'reduce'
  urgency: 'low' | 'medium' | 'high' | 'critical'
  reason: string
  recommended_order_qty: number
  generated_at: string
}

export interface InventoryRecommendationResponse extends ApiResponse<InventoryRecommendation> {}

export interface BatchRecommendationsResponse extends ApiResponse<{
  batch_size: number
  recommendations: InventoryRecommendation[]
  critical_count: number
  high_count: number
  generated_at: string
}> {}

export interface ReorderItem {
  item_id: number
  current_stock: number
  action: string
  urgency: string
  reason: string
  recommended_order_qty: number
}

export interface ReorderSummaryResponse extends ApiResponse<{
  summary_type: string
  items_needing_reorder: number
  total_reorder_quantity: number
  items: ReorderItem[]
  generated_at: string
}> {}

export interface InventoryStatusItem {
  item_id: number
  item_name: string
  current_stock: number
  projected_stock: number
  days_until_stockout: number
}

export interface InventoryStatusResponse extends ApiResponse<{
  report_type: string
  total_items: number
  status_summary: {
    healthy: number
    medium: number
    low: number
    critical: number
  }
  status_details: {
    healthy: InventoryStatusItem[]
    medium: InventoryStatusItem[]
    low: InventoryStatusItem[]
    critical: InventoryStatusItem[]
  }
  generated_at: string
}> {}

export interface WasteInsight {
  item_id: number
  item_name: string
  issue: string
  current_stock: number
  days_to_expiry?: number
  days_supply?: number
  recommendation: string
  potential_savings?: number
  potential_loss?: number
}

export interface WasteInsightsResponse extends ApiResponse<{
  analysis_type: string
  insights_count: number
  insights: WasteInsight[]
  generated_at: string
}> {}

export interface CostAnalysisItem {
  item_id: number
  item_name: string
  annual_demand: number
  holding_cost: number
  ordering_cost: number
  total_cost: number
}

export interface CostAnalysisResponse extends ApiResponse<{
  analysis_type: string
  total_items: number
  total_holding_cost: number
  total_ordering_cost: number
  total_inventory_cost: number
  items: CostAnalysisItem[]
  generated_at: string
}> {}

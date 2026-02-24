// frontend/src/utils/constants.ts

/**
 * API Configuration
 */
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/predictions',
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 2,
  RETRY_DELAY: 1000, // 1 second
}

/**
 * Cache Configuration
 */
export const CACHE_CONFIG = {
  DEMAND_FORECAST_STALE_TIME: 5 * 60 * 1000, // 5 minutes
  DEMAND_FORECAST_GC_TIME: 10 * 60 * 1000, // 10 minutes
  KITCHEN_PREDICTIONS_STALE_TIME: 3 * 60 * 1000, // 3 minutes
  KITCHEN_PREDICTIONS_GC_TIME: 10 * 60 * 1000, // 10 minutes
  CUSTOMER_ANALYTICS_STALE_TIME: 10 * 60 * 1000, // 10 minutes
  CUSTOMER_ANALYTICS_GC_TIME: 20 * 60 * 1000, // 20 minutes
  INVENTORY_STATUS_STALE_TIME: 5 * 60 * 1000, // 5 minutes
  INVENTORY_STATUS_GC_TIME: 15 * 60 * 1000, // 15 minutes
}

/**
 * Default Restaurant ID (for demo/testing)
 */
export const DEFAULT_RESTAURANT_ID = 'a33877ad-36ac-420a-96d0-6f518e5af21b'

/**
 * Forecast Types
 */
export const FORECAST_TYPES = {
  HOURLY: 'hourly',
  DAILY: 'daily',
} as const

/**
 * Time Windows
 */
export const TIME_WINDOWS = {
  HOURS_12: 12,
  HOURS_24: 24,
  HOURS_48: 48,
  DAYS_7: 7,
  DAYS_30: 30,
} as const

/**
 * Status Colors
 */
export const STATUS_COLORS = {
  SUCCESS: '#10B981',
  WARNING: '#F59E0B',
  ERROR: '#EF4444',
  INFO: '#06B6D4',
} as const

/**
 * Urgency Levels
 */
export const URGENCY_LEVELS = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical',
} as const

/**
 * Inventory Actions
 */
export const INVENTORY_ACTIONS = {
  MAINTAIN: 'maintain',
  REORDER: 'reorder',
  EMERGENCY_REORDER: 'emergency_reorder',
  REDUCE: 'reduce',
} as const

/**
 * Customer Risk Segments
 */
export const RISK_SEGMENTS = {
  LOW_RISK: 'low_risk',
  MEDIUM_RISK: 'medium_risk',
  HIGH_RISK: 'high_risk',
} as const

/**
 * LTV Segments
 */
export const LTV_SEGMENTS = {
  LOW_VALUE: 'low_value',
  MEDIUM_VALUE: 'medium_value',
  HIGH_VALUE: 'high_value',
} as const

/**
 * Chart Colors
 */
export const CHART_COLORS = {
  PRIMARY: '#3B82F6',
  SECONDARY: '#8B5CF6',
  ACCENT: '#EC4899',
  SUCCESS: '#10B981',
  WARNING: '#F59E0B',
  ERROR: '#EF4444',
  INFO: '#06B6D4',
} as const

/**
 * Date Formats
 */
export const DATE_FORMATS = {
  FULL: 'PPP p',
  DATE_ONLY: 'PPP',
  TIME_ONLY: 'p',
  SHORT_DATE: 'MMM d',
  SHORT_TIME: 'HH:mm',
} as const

/**
 * Pagination
 */
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_LIMIT: 10,
  MAX_LIMIT: 100,
} as const

/**
 * Error Messages
 */
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error - please check your connection',
  SERVER_ERROR: 'Server error - please try again later',
  NOT_FOUND: 'Resource not found',
  UNAUTHORIZED: 'Unauthorized - please log in',
  FORBIDDEN: 'Forbidden - you do not have permission',
  VALIDATION_ERROR: 'Validation error - please check your input',
  UNKNOWN_ERROR: 'An unexpected error occurred',
} as const

/**
 * Success Messages
 */
export const SUCCESS_MESSAGES = {
  LOADED: 'Data loaded successfully',
  SAVED: 'Data saved successfully',
  DELETED: 'Data deleted successfully',
  UPDATED: 'Data updated successfully',
} as const

/**
 * Menu Items (Sample Data)
 */
export const SAMPLE_MENU_ITEMS = [
  { id: 1, name: 'Burger', category: 'Burgers' },
  { id: 2, name: 'Cheeseburger', category: 'Burgers' },
  { id: 3, name: 'Fries', category: 'Sides' },
  { id: 4, name: 'Onion Rings', category: 'Sides' },
  { id: 5, name: 'Pizza Margherita', category: 'Pizzas' },
  { id: 6, name: 'Pepperoni Pizza', category: 'Pizzas' },
  { id: 7, name: 'Caesar Salad', category: 'Salads' },
  { id: 8, name: 'Greek Salad', category: 'Salads' },
  { id: 9, name: 'Spaghetti', category: 'Pasta' },
  { id: 10, name: 'Fettuccine', category: 'Pasta' },
] as const

/**
 * Menu Categories (Sample Data)
 */
export const SAMPLE_CATEGORIES = [
  'Burgers',
  'Sides',
  'Pizzas',
  'Salads',
  'Pasta',
  'Beverages',
  'Desserts',
] as const

/**
 * Kitchen Stations (Sample Data)
 */
export const SAMPLE_STATIONS = [
  { id: 1, name: 'Grill' },
  { id: 2, name: 'Fryer' },
  { id: 3, name: 'Prep' },
  { id: 4, name: 'Drinks Area' },
] as const

/**
 * Local Storage Keys
 */
export const STORAGE_KEYS = {
  THEME: 'theme-store',
  USER_PREFERENCES: 'user-preferences',
  RECENT_RESTAURANT: 'recent-restaurant-id',
  AUTH_TOKEN: 'auth-token',
} as const

/**
 * Feature Flags
 */
export const FEATURE_FLAGS = {
  ENABLE_REAL_TIME_UPDATES: false,
  ENABLE_EXPORT_PDF: true,
  ENABLE_EXPORT_CSV: true,
  ENABLE_NOTIFICATIONS: true,
  ENABLE_DARK_MODE: true,
  ENABLE_MULTI_THEME: true,
} as const

export default {
  API_CONFIG,
  CACHE_CONFIG,
  DEFAULT_RESTAURANT_ID,
  FORECAST_TYPES,
  TIME_WINDOWS,
  STATUS_COLORS,
  URGENCY_LEVELS,
  INVENTORY_ACTIONS,
  RISK_SEGMENTS,
  LTV_SEGMENTS,
  CHART_COLORS,
  DATE_FORMATS,
  PAGINATION,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
  SAMPLE_MENU_ITEMS,
  SAMPLE_CATEGORIES,
  SAMPLE_STATIONS,
  STORAGE_KEYS,
  FEATURE_FLAGS,
}

import { apiClient, handleApiError } from './api'
import {
    type DemandForecastResponse,
    type ItemDemandResponse,
    type PeakHoursResponse,
} from '../types/api'

/**
 * Demand Forecasting Service
 * Handles all demand prediction API calls
 */
export const demandService = {
    /**
     * Get hourly or daily demand forecast
     */
    forecast: async (
        restaurantId: string,
        forecastType: 'hourly' | 'daily' = 'hourly',
        hoursAhead: number = 24,
        daysAhead: number = 7,
    ): Promise<DemandForecastResponse> => {
        try {
            const payload = {
                restaurant_id: restaurantId,
                forecast_type: forecastType,
                ...(forecastType === 'hourly' && { hours_ahead: hoursAhead }),
                ...(forecastType === 'daily' && { days_ahead: daysAhead }),
            }
            return await apiClient.post('/demand', payload)
        } catch (error) {
            throw new Error(`Failed to fetch demand forecast: ${handleApiError(error)}`)
        }
    },

    /**
     * Get demand forecast for specific menu item
     */
    itemDemand: async (
        restaurantId: string,
        itemId: string,
        hoursAhead: number = 24
    ): Promise<ItemDemandResponse> => {
        try {
            return await apiClient.post(
                `/demand/items?restaurant_id=${restaurantId}&item_id=${itemId}&hours_ahead=${hoursAhead}`
            )
        } catch (error) {
            throw new Error(`Failed to fetch item demand: ${handleApiError(error)}`)
        }
    },

    /**
     * Get demand forecast for menu category
     */
    categoryDemand: async (
        restaurantId: string,
        categoryName: string,
        hoursAhead: number = 24
    ): Promise<ItemDemandResponse> => {
        try {
            return await apiClient.post(
                `/demand/category?restaurant_id=${restaurantId}&category_name=${categoryName}&hours_ahead=${hoursAhead}`
            )
        } catch (error) {
            throw new Error(`Failed to fetch category demand: ${handleApiError(error)}`)
        }
    },

    /**
     * Get peak hours analysis
     */
    peakHours: async (
        restaurantId: string,
        daysAhead: number = 7
    ): Promise<PeakHoursResponse> => {
        try {
            return await apiClient.get(
                `/demand/peak-hours?restaurant_id=${restaurantId}&days_ahead=${daysAhead}`
            )
        } catch (error) {
            throw new Error(`Failed to fetch peak hours: ${handleApiError(error)}`)
        }
    },
}

export default demandService
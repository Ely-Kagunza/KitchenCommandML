import { useQuery, type UseQueryResult } from '@tanstack/react-query'
import { demandService } from '../services/demand'
import { 
    type DemandForecastResponse,
    type ItemDemandResponse,
    type PeakHoursResponse,
 } from '../types/api'

 /**
  * Hook for fetching hourly/daily demand forecast
  */
export const useDemandForecast = (
    restaurantId: string,
    forecastType: 'hourly' | 'daily' = 'hourly',
    hoursAhead: number = 24,
    daysAhead: number = 7,
    enabled: boolean = true
): UseQueryResult<DemandForecastResponse, Error> => {
    return useQuery({
        queryKey: ['demand-forecast', restaurantId, forecastType, hoursAhead, daysAhead],
        queryFn: () => demandService.forecast(restaurantId, forecastType, hoursAhead, daysAhead),
        staleTime: 5 * 60 * 1000, // 5 minutes
        gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
        enabled: !!restaurantId && enabled,
        retry: 2,
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    })
}

/**
 * Hook for fetching item-level demand
 */
export const useItemDemand = (
    restaurantId: string,
    itemId: number,
    hoursAhead: number = 24,
    enabled: boolean = true
): UseQueryResult<ItemDemandResponse, Error> => {
    return useQuery({
        queryKey: ['item-demand', restaurantId, itemId, hoursAhead],
        queryFn: () => demandService.itemDemand(restaurantId, itemId.toString(), hoursAhead),
        staleTime: 5 * 60 * 1000, // 5 minutes
        gcTime: 10 * 60 * 1000, // 10 minutes
        enabled: !!restaurantId && !!itemId && enabled,
        retry: 2,
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    })
}

/**
 * Hook for fetching category-level demand
 */
export const useCategoryDemand = (
    restaurantId: string,
    categoryName: string,
    hoursAhead: number = 24,
    enabled: boolean = true
): UseQueryResult<ItemDemandResponse, Error> => {
    return useQuery({
        queryKey: ['category-demand', restaurantId, categoryName, hoursAhead],
        queryFn: () => demandService.categoryDemand(restaurantId, categoryName, hoursAhead),
        staleTime: 5 * 60 * 1000, // 5 minutes
        gcTime: 10 * 60 * 1000, // 10 minutes
        enabled: !!restaurantId && !!categoryName && enabled,
        retry: 2,
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    })
}

/**
 * Hook for fetching peak hours analysis
 */
export const usePeakHours = (
    restaurantId: string,
    daysAhead: number = 7,
    enabled: boolean = true
): UseQueryResult<PeakHoursResponse, Error> => {
    return useQuery({
        queryKey: ['peak-hours', restaurantId, daysAhead],
        queryFn: () => demandService.peakHours(restaurantId, daysAhead),
        staleTime: 5 * 60 * 1000, // 5 minutes
        gcTime: 10 * 60 * 1000, // 10 minutes
        enabled: !!restaurantId && enabled,
        retry: 2,
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    })
}
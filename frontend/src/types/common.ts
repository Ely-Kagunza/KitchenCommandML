// frontend/src/types/common.ts

export interface ApiResponse<T> {
  success: boolean
  data: T
  metadata: {
    model_version: string
    prediction_time_ms: number
    generated_at: string
  }
}

export interface ApiError {
  detail: string
}

export interface LoadingState {
  isLoading: boolean
  error: string | null
  data: unknown | null
}

export interface PaginationParams {
  page: number
  limit: number
}

export interface DateRange {
  startDate: string
  endDate: string
}

export type RestaurantId = string

export interface AsyncState<T> {
  data: T | null
  loading: boolean
  error: Error | null
}

import axios, { type AxiosInstance, type AxiosError } from 'axios'
import type { ApiError } from '../types/common'

/**
 * API Base URL from environment or default
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/predictions'

/**
 * Create Axios instance with default configuration
 */
export const apiClient: AxiosInstance = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000, // 30 seconds timeout
})

/**
 * Request interceptor to handle API errors
 */
apiClient.interceptors.request.use(
    (config) => {
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

/**
 * Response interceptor to handle API errors
 */
apiClient.interceptors.response.use(
    (response) => {
        return response.data
    },
    (error: AxiosError<ApiError>) => {
        // Handle common errors
        if (error.response?.status === 404) {
            console.error('Resource not found:', error.response.data?.detail)
        } else if (error.response?.status === 500) {
            console.error('Internal server error:', error.response.data?.detail)
        } else if (error.message === 'Network Error') {
            console.error('Network error - check your internet connection')
        }
        return Promise.reject(error)
    }
)

/**
 * Helper function to handle API errors
 */
export const handleApiError = (error: unknown): string => {
    if (axios.isAxiosError(error)) {
        if (error.response?.data?.detail) {
            return error.response.data.detail
        }
        if (error.message) {
            return error.message
        }
    }
    return 'An unknown error occurred'
}

/**
 * Helper function to check if API is available
 */
export const checkApiHealth = async (): Promise<boolean> => {
    try {
        const response = await axios.get(`${API_BASE_URL.replace('/api/predictions', '')}/health`)
        return response.status === 200
    } catch {
        return false
    }
}

export default apiClient
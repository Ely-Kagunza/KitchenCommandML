// frontend/src/utils/formatters.ts

import { format, formatDistanceToNow, parseISO } from 'date-fns'

/**
 * Format number as currency
 */
export const formatCurrency = (value: number, currency: string = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
  }).format(value)
}

/**
 * Format number with thousand separators
 */
export const formatNumber = (value: number, decimals: number = 0): string => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
}

/**
 * Format percentage
 */
export const formatPercentage = (value: number, decimals: number = 1): string => {
  return `${formatNumber(value * 100, decimals)}%`
}

/**
 * Format date to readable string
 */
export const formatDate = (date: string | Date, formatStr: string = 'PPP'): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    return format(dateObj, formatStr)
  } catch {
    return 'Invalid date'
  }
}

/**
 * Format date and time
 */
export const formatDateTime = (date: string | Date): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    return format(dateObj, 'PPP p')
  } catch {
    return 'Invalid date'
  }
}

/**
 * Format time only
 */
export const formatTime = (date: string | Date): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    return format(dateObj, 'HH:mm:ss')
  } catch {
    return 'Invalid time'
  }
}

/**
 * Format date relative to now (e.g., "2 hours ago")
 */
export const formatRelativeTime = (date: string | Date): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    return formatDistanceToNow(dateObj, { addSuffix: true })
  } catch {
    return 'Invalid date'
  }
}

/**
 * Format duration in milliseconds to readable string
 */
export const formatDuration = (ms: number): string => {
  if (ms < 1000) {
    return `${ms}ms`
  } else if (ms < 60000) {
    return `${(ms / 1000).toFixed(2)}s`
  } else {
    return `${(ms / 60000).toFixed(2)}m`
  }
}

/**
 * Format bytes to human readable size
 */
export const formatBytes = (bytes: number, decimals: number = 2): string => {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

/**
 * Format phone number
 */
export const formatPhoneNumber = (phone: string): string => {
  const cleaned = phone.replace(/\D/g, '')
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`
  }
  return phone
}

/**
 * Format email (truncate if too long)
 */
export const formatEmail = (email: string, maxLength: number = 30): string => {
  if (email.length > maxLength) {
    return email.substring(0, maxLength - 3) + '...'
  }
  return email
}

/**
 * Format text to title case
 */
export const formatTitleCase = (text: string): string => {
  return text
    .toLowerCase()
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

/**
 * Format text to sentence case
 */
export const formatSentenceCase = (text: string): string => {
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase()
}

/**
 * Format text to kebab case
 */
export const formatKebabCase = (text: string): string => {
  return text
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^\w-]/g, '')
}

/**
 * Format text to snake case
 */
export const formatSnakeCase = (text: string): string => {
  return text
    .toLowerCase()
    .replace(/\s+/g, '_')
    .replace(/[^\w_]/g, '')
}

/**
 * Truncate text with ellipsis
 */
export const truncateText = (text: string, maxLength: number = 50): string => {
  if (text.length > maxLength) {
    return text.substring(0, maxLength - 3) + '...'
  }
  return text
}

/**
 * Format array to comma-separated string
 */
export const formatArray = (arr: string[], maxItems: number = 3): string => {
  if (arr.length <= maxItems) {
    return arr.join(', ')
  }
  return arr.slice(0, maxItems).join(', ') + ` +${arr.length - maxItems} more`
}

/**
 * Format status badge text
 */
export const formatStatusBadge = (status: string): string => {
  return formatTitleCase(status.replace(/_/g, ' '))
}

/**
 * Format urgency level
 */
export const formatUrgency = (urgency: string): string => {
  const urgencyMap: Record<string, string> = {
    low: '🟢 Low',
    medium: '🟡 Medium',
    high: '🔴 High',
    critical: '⛔ Critical',
  }
  return urgencyMap[urgency.toLowerCase()] || urgency
}

/**
 * Format action type
 */
export const formatAction = (action: string): string => {
  const actionMap: Record<string, string> = {
    maintain: '✅ Maintain',
    reorder: '📦 Reorder',
    emergency_reorder: '🚨 Emergency Reorder',
    reduce: '📉 Reduce',
  }
  return actionMap[action.toLowerCase()] || formatTitleCase(action)
}

/**
 * Format risk segment
 */
export const formatRiskSegment = (segment: string): string => {
  const segmentMap: Record<string, string> = {
    low_risk: '🟢 Low Risk',
    medium_risk: '🟡 Medium Risk',
    high_risk: '🔴 High Risk',
  }
  return segmentMap[segment.toLowerCase()] || formatTitleCase(segment)
}

/**
 * Format LTV segment
 */
export const formatLTVSegment = (segment: string): string => {
  const segmentMap: Record<string, string> = {
    low_value: '💰 Low Value',
    medium_value: '💵 Medium Value',
    high_value: '💎 High Value',
  }
  return segmentMap[segment.toLowerCase()] || formatTitleCase(segment)
}

/**
 * Format confidence score
 */
export const formatConfidence = (confidence: number): string => {
  const percentage = Math.round(confidence * 100)
  if (percentage >= 90) return '🟢 Very High'
  if (percentage >= 75) return '🟢 High'
  if (percentage >= 60) return '🟡 Medium'
  if (percentage >= 40) return '🟠 Low'
  return '🔴 Very Low'
}

export default {
  formatCurrency,
  formatNumber,
  formatPercentage,
  formatDate,
  formatDateTime,
  formatTime,
  formatRelativeTime,
  formatDuration,
  formatBytes,
  formatPhoneNumber,
  formatEmail,
  formatTitleCase,
  formatSentenceCase,
  formatKebabCase,
  formatSnakeCase,
  truncateText,
  formatArray,
  formatStatusBadge,
  formatUrgency,
  formatAction,
  formatRiskSegment,
  formatLTVSegment,
  formatConfidence,
}

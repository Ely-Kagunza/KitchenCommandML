import { describe, it, expect } from 'vitest'
import { DEFAULT_RESTAURANT_ID, FORECAST_TYPES, TIME_WINDOWS } from '../constants'

describe('Constants', () => {
  it('should have valid DEFAULT_RESTAURANT_ID', () => {
    expect(DEFAULT_RESTAURANT_ID).toBeDefined()
    expect(typeof DEFAULT_RESTAURANT_ID).toBe('string')
    expect(DEFAULT_RESTAURANT_ID.length).toBeGreaterThan(0)
  })

  it('should have valid FORECAST_TYPES', () => {
    expect(FORECAST_TYPES.HOURLY).toBe('hourly')
    expect(FORECAST_TYPES.DAILY).toBe('daily')
  })

  it('should have valid TIME_WINDOWS', () => {
    expect(TIME_WINDOWS.HOURS_12).toBe(12)
    expect(TIME_WINDOWS.HOURS_24).toBe(24)
    expect(TIME_WINDOWS.HOURS_48).toBe(48)
    expect(TIME_WINDOWS.DAYS_7).toBe(7)
    expect(TIME_WINDOWS.DAYS_30).toBe(30)
  })
})

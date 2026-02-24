import React, { useState } from 'react'
import {
    LineChart,
    Line,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer
} from 'recharts'
import { useDemandForecast } from '../../hooks/useDemandForecast'
import { useThemeStore } from '../../stores/themeStore'

interface DemandForecastProps {
    restaurantId: string
}

/**
 * Demand Forecast Component
 * Displays hourly and daily demand predictions
 */
export const DemandForecast: React.FC<DemandForecastProps> = ({ restaurantId }) => {
    const [forecastType, setForecastType] = useState<'hourly' | 'daily'>('hourly')
    const { currentTheme } = useThemeStore()

    const { data, isLoading, error } = useDemandForecast(
        restaurantId,
        forecastType,
        24,
        7
    )

    if (isLoading) {
      return (
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2" 
               style={{ borderColor: currentTheme.colors.primary }}>
          </div>
        </div>
      )
    }

    if (error) {
      return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 font-semibold">Error loading forecast</p>
          <p className="text-red-600 text-sm">{error.message}</p>
        </div>
      )
    }

    if (!data?.data?.predictions) {
      return (
        <div className="text-center py-8">
          <p className="text-gray-500">No forecast data available</p>
        </div>
      )
    }

    const predictions = data.data.predictions

    return (
      <div
        className="rounded-xl shadow-md border p-6"
        style={{
          backgroundColor: currentTheme.colors.surface,
          borderColor: currentTheme.colors.border,
        }}
      >
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div className="flex items-center">
            <div
              className="h-14 w-14 rounded-xl flex items-center justify-center mr-4"
              style={{ backgroundColor: `${currentTheme.colors.primary}20` }}
            >
              <span className="text-2xl">📊</span>
            </div>
            <div>
              <h2 className="text-xl font-semibold" style={{ color: currentTheme.colors.text }}>
                Demand Forecast
              </h2>
              <p className="text-sm mt-0.5" style={{ color: currentTheme.colors.textSecondary }}>
                {forecastType === 'hourly' ? 'Next 24 Hours' : 'Next 7 Days'}
              </p>
            </div>
          </div>
  
          {/* Toggle Buttons */}
          <div className="flex gap-2">
            <button
              onClick={() => setForecastType('hourly')}
              className="px-5 py-2.5 rounded-lg font-medium transition-all cursor-pointer hover:shadow-md"
              style={
                forecastType === 'hourly'
                  ? {
                      backgroundColor: currentTheme.colors.primary,
                      color: currentTheme.colors.textInverse,
                    }
                  : {
                      backgroundColor: currentTheme.colors.backgroundSecondary,
                      color: currentTheme.colors.textSecondary,
                      border: `1px solid ${currentTheme.colors.border}`,
                    }
              }
            >
              Hourly
            </button>
            <button
              onClick={() => setForecastType('daily')}
              className="px-5 py-2.5 rounded-lg font-medium transition-all cursor-pointer hover:shadow-md"
              style={
                forecastType === 'daily'
                  ? {
                      backgroundColor: currentTheme.colors.primary,
                      color: currentTheme.colors.textInverse,
                    }
                  : {
                      backgroundColor: currentTheme.colors.backgroundSecondary,
                      color: currentTheme.colors.textSecondary,
                      border: `1px solid ${currentTheme.colors.border}`,
                    }
              }
            >
              Daily
            </button>
          </div>
        </div>
  
        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          <div
            className="rounded-xl p-5 border overflow-hidden"
            style={{
              background: `linear-gradient(to bottom right, ${currentTheme.colors.primaryLight}, ${currentTheme.colors.primary}10)`,
              borderColor: currentTheme.colors.primary,
            }}
          >
            <p
              className="text-xs uppercase tracking-wide font-semibold mb-2"
              style={{ color: currentTheme.colors.textSecondary }}
            >
              Total Predicted Orders
            </p>
            <p className="text-3xl font-bold leading-tight" style={{ color: currentTheme.colors.primary }}>
              {predictions.reduce((sum, p) => sum + p.predicted_orders, 0)}
            </p>
          </div>
          <div
            className="rounded-xl p-5 border overflow-hidden"
            style={{
              background: `linear-gradient(to bottom right, ${currentTheme.colors.successLight}, ${currentTheme.colors.success}10)`,
              borderColor: currentTheme.colors.success,
            }}
          >
            <p
              className="text-xs uppercase tracking-wide font-semibold mb-2"
              style={{ color: currentTheme.colors.textSecondary }}
            >
              Average Orders
            </p>
            <p className="text-3xl font-bold leading-tight" style={{ color: currentTheme.colors.success }}>
              {Math.round(
                predictions.reduce((sum, p) => sum + p.predicted_orders, 0) /
                  predictions.length
              )}
            </p>
          </div>
          <div
            className="rounded-xl p-5 border overflow-hidden"
            style={{
              background: `linear-gradient(to bottom right, ${currentTheme.colors.secondaryLight}, ${currentTheme.colors.secondary}10)`,
              borderColor: currentTheme.colors.secondary,
            }}
          >
            <p
              className="text-xs uppercase tracking-wide font-semibold mb-2"
              style={{ color: currentTheme.colors.textSecondary }}
            >
              Peak Orders
            </p>
            <p className="text-3xl font-bold leading-tight" style={{ color: currentTheme.colors.secondary }}>
              {Math.max(...predictions.map((p) => p.predicted_orders))}
            </p>
          </div>
        </div>
  
        {/* Chart */}
        <div className="w-full h-96">
          <ResponsiveContainer width="100%" height="100%">
            {forecastType === 'hourly' ? (
              <LineChart data={predictions}>
                <CartesianGrid strokeDasharray="3 3" stroke={currentTheme.colors.border} />
                <XAxis
                  dataKey="timestamp"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).getHours() + ':00'}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: currentTheme.colors.surface,
                    border: `1px solid ${currentTheme.colors.border}`,
                  }}
                  formatter={(value) => [`${value} orders`, 'Predicted']}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="predicted_orders"
                  stroke={currentTheme.colors.primary}
                  strokeWidth={2}
                  dot={{ fill: currentTheme.colors.primary, r: 4 }}
                  activeDot={{ r: 6 }}
                  name="Predicted Orders"
                />
              </LineChart>
            ) : (
              <BarChart data={predictions}>
                <CartesianGrid strokeDasharray="3 3" stroke={currentTheme.colors.border} />
                <XAxis
                  dataKey="timestamp"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                  })}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: currentTheme.colors.surface,
                    border: `1px solid ${currentTheme.colors.border}`,
                  }}
                  formatter={(value) => [`${value} orders`, 'Predicted']}
                />
                <Legend />
                <Bar
                  dataKey="predicted_orders"
                  fill={currentTheme.colors.primary}
                  name="Predicted Orders"
                  radius={[8, 8, 0, 0]}
                />
              </BarChart>
            )}
          </ResponsiveContainer>
        </div>
  
        {/* Metadata */}
        <div
          className="mt-6 pt-6 border-t text-sm"
          style={{
            borderColor: currentTheme.colors.border,
            color: currentTheme.colors.textTertiary,
          }}
        >
          <div className="flex justify-between">
            <span>Generated: {new Date(data.metadata.generated_at).toLocaleString()}</span>
            <span>Prediction Time: {data.metadata.prediction_time_ms}ms</span>
          </div>
        </div>
      </div>
    )
  }
  
  export default DemandForecast
// frontend/src/components/demand/PeakHours.tsx

import React from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { usePeakHours } from '../../hooks/useDemandForecast'
import { useThemeStore } from '../../stores/themeStore'

interface PeakHoursProps {
  restaurantId: string
  daysAhead?: number
}

/**
 * Peak Hours Component
 * Displays peak hours analysis for next N days
 */
export const PeakHours: React.FC<PeakHoursProps> = ({ restaurantId, daysAhead = 7 }) => {
  const { currentTheme } = useThemeStore()
  const { data, isLoading, error } = usePeakHours(restaurantId, daysAhead)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-80">
        <div
          className="animate-spin rounded-full h-12 w-12 border-b-2"
          style={{ borderColor: currentTheme.colors.primary }}
        ></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800 font-semibold">Error loading peak hours</p>
        <p className="text-red-600 text-sm">{error.message}</p>
      </div>
    )
  }

  if (!data?.data?.analysis) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No peak hours data available</p>
      </div>
    )
  }

  // Transform data for chart
  const chartData = data.data.analysis.map((day) => {
    const dayData: any = {
      date: new Date(day.date).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      }),
    }

    day.peak_hours.forEach((hour, index) => {
      dayData[`hour_${hour.hour}`] = hour.predicted_orders
    })

    return dayData
  })

  return (
    <div
      className="w-full rounded-xl shadow-md border p-6 mb-8" /* card spacing */
      style={{
        backgroundColor: currentTheme.colors.surface,
        borderColor: currentTheme.colors.border,
      }}
    >
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center">
          <div
            className="h-10 w-10 rounded-lg flex items-center justify-center mr-3"
            style={{ backgroundColor: `${currentTheme.colors.primary}20` }}
          >
            <span className="text-xl">⏱️</span>
          </div>
          <div>
            <h2 className="text-2xl font-bold" style={{ color: currentTheme.colors.text }}>
              Peak Hours Analysis
            </h2>
            <p className="text-sm" style={{ color: currentTheme.colors.textSecondary }}>
              Top 3 peak hours for next {daysAhead} days
            </p>
          </div>
        </div>
      </div>

      {/* Peak Hours Table */}
      <div className="mb-8 overflow-x-auto"> /* more bottom space before chart */
        <table className="w-full text-sm">
          <thead>
            <tr style={{ borderBottom: `2px solid ${currentTheme.colors.border}` }}>
              <th className="text-left py-3 px-4" style={{ color: currentTheme.colors.text }}>
                Date
              </th>
              <th className="text-center py-3 px-4" style={{ color: currentTheme.colors.text }}>
                Peak Hour 1
              </th>
              <th className="text-center py-3 px-4" style={{ color: currentTheme.colors.text }}>
                Peak Hour 2
              </th>
              <th className="text-center py-3 px-4" style={{ color: currentTheme.colors.text }}>
                Peak Hour 3
              </th>
            </tr>
          </thead>
          <tbody>
            {data.data.analysis.map((day, index) => (
              <tr
                key={index}
                className="hover:bg-opacity-10 hover:bg-gray-200 transition-colors"
                style={{
                  borderBottom: `1px solid ${currentTheme.colors.border}`,
                  backgroundColor: index % 2 === 0 ? currentTheme.colors.surface : 'transparent',
                }}
              >
                <td className="py-3 px-4" style={{ color: currentTheme.colors.text }}>
                  {new Date(day.date).toLocaleDateString('en-US', {
                    weekday: 'short',
                    month: 'short',
                    day: 'numeric',
                  })}
                </td>
                {day.peak_hours.map((hour, hourIndex) => (
                  <td key={hourIndex} className="text-center py-3 px-4">
                    <div className="flex flex-col items-center">
                      <span
                        className="font-bold text-lg"
                        style={{ color: currentTheme.colors.primary }}
                      >
                        {hour.hour}:00
                      </span>
                      <span
                        className="text-xs"
                        style={{ color: currentTheme.colors.textSecondary }}
                      >
                        {hour.predicted_orders} orders
                      </span>
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Chart */}
      <div className="w-full mb-8" style={{ height: '320px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke={currentTheme.colors.border} />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip
              contentStyle={{
                backgroundColor: currentTheme.colors.surface,
                border: `1px solid ${currentTheme.colors.border}`,
              }}
              formatter={(value) => [`${value} orders`, 'Peak Hour']}
            />
            <Legend />
            {data.data.analysis[0]?.peak_hours.map((_, index) => (
              <Bar
                key={index}
                dataKey={`hour_${data.data.analysis[0].peak_hours[index].hour}`}
                fill={
                  index === 0
                    ? currentTheme.colors.primary
                    : index === 1
                    ? currentTheme.colors.secondary
                    : currentTheme.colors.accent
                }
                name={`Peak ${index + 1}`}
                radius={[8, 8, 0, 0]}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Metadata */}
      <div className="mt-4 text-xs" style={{ color: currentTheme.colors.textTertiary }}>
        <p>Generated: {new Date(data.metadata.generated_at).toLocaleString()}</p>
        <p>Prediction Time: {data.metadata.prediction_time_ms}ms</p>
      </div>
    </div>
  )
}

export default PeakHours

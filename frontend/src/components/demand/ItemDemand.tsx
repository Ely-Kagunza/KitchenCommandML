// frontend/src/components/demand/ItemDemand.tsx

import React, { useState } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { useItemDemand } from '../../hooks/useDemandForecast'
import { useThemeStore } from '../../stores/themeStore'

interface ItemDemandProps {
  restaurantId: string
  itemId: number
  itemName?: string
}

/**
 * Item Demand Component
 * Displays demand predictions for a specific menu item
 */
export const ItemDemand: React.FC<ItemDemandProps> = ({
  restaurantId,
  itemId,
  itemName = 'Menu Item',
}) => {
  const [hoursAhead, setHoursAhead] = useState(24)
  const { currentTheme } = useThemeStore()

  const { data, isLoading, error } = useItemDemand(restaurantId, itemId, hoursAhead)

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
        <p className="text-red-800 font-semibold">Error loading item demand</p>
        <p className="text-red-600 text-sm">{error.message}</p>
      </div>
    )
  }

  if (!data?.data?.predictions) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No item demand data available</p>
      </div>
    )
  }

  const predictions = data.data.predictions
  const totalOrders = predictions.reduce((sum, p) => sum + p.predicted_orders, 0)
  const avgOrders = Math.round(totalOrders / predictions.length)
  const maxOrders = Math.max(...predictions.map((p) => p.predicted_orders))

  return (
    <div
      className="w-full rounded-xl shadow-md border p-6"
      style={{
        backgroundColor: currentTheme.colors.surface,
        borderColor: currentTheme.colors.border,
      }}
    >
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center">
          <div
            className="h-10 w-10 rounded-lg flex items-center justify-center mr-3"
            style={{ backgroundColor: `${currentTheme.colors.primary}20` }}
          >
            <span className="text-xl">🍔</span>
          </div>
          <div>
            <h2 className="text-2xl font-bold" style={{ color: currentTheme.colors.text }}>
              {data.data.item_name || itemName}
            </h2>
            <p className="text-sm" style={{ color: currentTheme.colors.textSecondary }}>
              Item-level demand forecast
            </p>
          </div>
        </div>

        {/* Hours Selector */}
        <div className="flex gap-2">
          {[12, 24, 48].map((hours) => (
            <button
              key={hours}
              onClick={() => setHoursAhead(hours)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors cursor-pointer hover:shadow-md ${
                hoursAhead === hours ? 'text-white' : 'text-gray-600 bg-gray-100'
              }`}
              style={
                hoursAhead === hours
                  ? { backgroundColor: currentTheme.colors.primary }
                  : {}
              }
            >
              {hours}h
            </button>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="rounded-lg p-4 hover:shadow-lg transition-all cursor-pointer" style={{ backgroundColor: currentTheme.colors.primaryLight }}>
          <p className="text-sm" style={{ color: currentTheme.colors.textSecondary }}>
            Total Orders
          </p>
          <p className="text-2xl font-bold" style={{ color: currentTheme.colors.primary }}>
            {totalOrders}
          </p>
        </div>
        <div className="rounded-lg p-4 hover:shadow-lg transition-all cursor-pointer" style={{ backgroundColor: currentTheme.colors.successLight }}>
          <p className="text-sm" style={{ color: currentTheme.colors.textSecondary }}>
            Average Orders
          </p>
          <p className="text-2xl font-bold" style={{ color: currentTheme.colors.success }}>
            {avgOrders}
          </p>
        </div>
        <div className="rounded-lg p-4 hover:shadow-lg transition-all cursor-pointer" style={{ backgroundColor: currentTheme.colors.accentLight }}>
          <p className="text-sm" style={{ color: currentTheme.colors.textSecondary }}>
            Peak Orders
          </p>
          <p className="text-2xl font-bold" style={{ color: currentTheme.colors.accent }}>
            {maxOrders}
          </p>
        </div>
      </div>

      {/* Chart */}
      <div className="w-full h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={predictions}>
            <CartesianGrid strokeDasharray="3 3" stroke={currentTheme.colors.border} />
            <XAxis
              dataKey="timestamp"
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => new Date(value).toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
              })}
            />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip
              contentStyle={{
                backgroundColor: currentTheme.colors.surface,
                border: `1px solid ${currentTheme.colors.border}`,
              }}
              formatter={(value) => [`${value} orders`, 'Predicted']}
              labelFormatter={(label) =>
                new Date(label).toLocaleString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })
              }
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="predicted_orders"
              stroke={currentTheme.colors.primary}
              strokeWidth={3}
              dot={{ fill: currentTheme.colors.primary, r: 5 }}
              activeDot={{ r: 7 }}
              name="Predicted Orders"
              isAnimationActive={true}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Insights */}
      <div className="mt-6 grid grid-cols-2 gap-4">
        <div
          className="rounded-lg p-4"
          style={{ backgroundColor: currentTheme.colors.infoLight }}
        >
          <p className="text-sm font-semibold" style={{ color: currentTheme.colors.info }}>
            📊 Demand Trend
          </p>
          <p className="text-xs mt-2" style={{ color: currentTheme.colors.textSecondary }}>
            {totalOrders > avgOrders * predictions.length * 0.8
              ? 'High demand expected'
              : 'Moderate demand expected'}
          </p>
        </div>
        <div
          className="rounded-lg p-4"
          style={{ backgroundColor: currentTheme.colors.warningLight }}
        >
          <p className="text-sm font-semibold" style={{ color: currentTheme.colors.warning }}>
            ⚠️ Peak Time
          </p>
          <p className="text-xs mt-2" style={{ color: currentTheme.colors.textSecondary }}>
            Peak at {maxOrders} orders
          </p>
        </div>
      </div>

      {/* Metadata */}
      <div className="mt-4 text-xs" style={{ color: currentTheme.colors.textTertiary }}>
        <p>Generated: {new Date(data.metadata.generated_at).toLocaleString()}</p>
        <p>Prediction Time: {data.metadata.prediction_time_ms}ms</p>
      </div>
    </div>
  )
}

export default ItemDemand

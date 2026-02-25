// frontend/src/pages/DemandPage.tsx

import React, { useState } from 'react'
import { DemandForecast } from '../components/demand/DemandForecast'
import { PeakHours } from '../components/demand/PeakHours'
import { ItemDemand } from '../components/demand/ItemDemand'
import { CategoryDemand } from '../components/demand/CategoryDemand'
import { ThemeSelector } from '../components/common/ThemeSelector'
import { useThemeStore } from '../stores/themeStore'

interface DemandPageProps {
  restaurantId: string
}

/**
 * Demand Page
 * Main page for demand forecasting features
 */
export const DemandPage: React.FC<DemandPageProps> = ({ restaurantId }) => {
  const { currentTheme } = useThemeStore()
  const [activeTab, setActiveTab] = useState<'overview' | 'items' | 'categories' | 'peaks'>(
    'overview'
  )
  const [selectedItemId, setSelectedItemId] = useState<number>(1)
  const [selectedCategory, setSelectedCategory] = useState<string>('Burgers')

  // Sample menu items and categories
  const menuItems = [
    { id: 1, name: 'Burger', category: 'Burgers' },
    { id: 2, name: 'Fries', category: 'Sides' },
    { id: 3, name: 'Pizza', category: 'Pizzas' },
    { id: 4, name: 'Salad', category: 'Salads' },
    { id: 5, name: 'Pasta', category: 'Pasta' },
  ]

  const categories = ['Burgers', 'Sides', 'Pizzas', 'Salads', 'Pasta', 'Beverages']

  return (
    <div className="min-h-screen" style={{ backgroundColor: currentTheme.colors.background }}>
      {/* Top Navigation Bar */}
      <nav
        className="border-b"
        style={{
          backgroundColor: currentTheme.colors.surface,
          borderColor: currentTheme.colors.border,
        }}
      >
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div
                className="h-14 w-14 rounded-xl flex items-center justify-center mr-4"
                style={{ backgroundColor: currentTheme.colors.primary }}
              >
                <span className="text-2xl">🍽️</span>
              </div>
              <div>
                <h1 className="text-xl font-semibold" style={{ color: currentTheme.colors.text }}>
                  Kitchen ML Dashboard
                </h1>
                <p className="text-sm mt-0.5" style={{ color: currentTheme.colors.textSecondary }}>
                  Intelligent demand forecasting and analytics
                </p>
              </div>
            </div>
            
            <ThemeSelector />
          </div>
        </div>
      </nav>

      {/* Main Container */}
      <div className="space-y-8 p-6">
        <div className="max-w-7xl mx-auto">
          {/* Page Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
            <div>
              <h1 className="text-3xl font-bold" style={{ color: currentTheme.colors.text }}>
                Demand Forecasting
              </h1>
              <p className="text-sm mt-1" style={{ color: currentTheme.colors.textSecondary }}>
                Analyze and predict customer demand patterns to optimize operations
              </p>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="flex gap-2 mb-6 overflow-auto">
            {[
              { id: 'overview', label: 'Overview', icon: '📈' },
              { id: 'items', label: 'Menu Items', icon: '🍔' },
              { id: 'categories', label: 'Categories', icon: '📂' },
              { id: 'peaks', label: 'Peak Hours', icon: '⏰' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className="px-5 py-2.5 rounded-lg font-medium transition-all cursor-pointer hover:shadow-md"
                style={
                  activeTab === tab.id
                    ? {
                        backgroundColor: currentTheme.colors.primary,
                        color: currentTheme.colors.textInverse,
                        border: `1px solid ${currentTheme.colors.primary}`,
                      }
                    : {
                        backgroundColor: currentTheme.colors.surface,
                        color: currentTheme.colors.textSecondary,
                        border: `1px solid ${currentTheme.colors.border}`,
                      }
                }
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div>
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <DemandForecast restaurantId={restaurantId} />
            )}

            {/* Items Tab */}
            {activeTab === 'items' && (
              <div className="space-y-6">
                {/* Item Selector Card */}
                <div
                  className="rounded-xl shadow-md border p-6"
                  style={{
                    backgroundColor: currentTheme.colors.surface,
                    borderColor: currentTheme.colors.border,
                  }}
                >
                  <h3 className="text-lg font-semibold mb-4" style={{ color: currentTheme.colors.text }}>
                    Select Menu Item
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
                    {menuItems.map((item) => (
                      <button
                        key={item.id}
                        onClick={() => setSelectedItemId(item.id)}
                        className="group rounded-xl shadow-md border p-5 flex flex-col justify-between min-h-[100px] hover:shadow-lg transition-all cursor-pointer"
                        style={
                          selectedItemId === item.id
                            ? {
                                backgroundColor: currentTheme.colors.primary,
                                borderColor: currentTheme.colors.primary,
                                color: currentTheme.colors.textInverse,
                              }
                            : {
                                backgroundColor: currentTheme.colors.surface,
                                borderColor: currentTheme.colors.border,
                                color: currentTheme.colors.text,
                              }
                        }
                      >
                        <p className="text-base font-semibold">{item.name}</p>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Item Demand Chart */}
                <ItemDemand
                  restaurantId={restaurantId}
                  itemId={selectedItemId}
                  itemName={menuItems.find((i) => i.id === selectedItemId)?.name}
                />
              </div>
            )}

            {/* Categories Tab */}
            {activeTab === 'categories' && (
              <div className="space-y-6">
                {/* Category Selector Card */}
                <div
                  className="rounded-xl shadow-md border p-6"
                  style={{
                    backgroundColor: currentTheme.colors.surface,
                    borderColor: currentTheme.colors.border,
                  }}
                >
                  <h3 className="text-lg font-semibold mb-4" style={{ color: currentTheme.colors.text }}>
                    Select Category
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
                    {categories.map((category) => (
                      <button
                        key={category}
                        onClick={() => setSelectedCategory(category)}
                        className="group rounded-xl shadow-md border p-5 flex flex-col justify-between min-h-[100px] hover:shadow-lg transition-all cursor-pointer"
                        style={
                          selectedCategory === category
                            ? {
                                backgroundColor: currentTheme.colors.secondary,
                                borderColor: currentTheme.colors.secondary,
                                color: currentTheme.colors.textInverse,
                              }
                            : {
                                backgroundColor: currentTheme.colors.surface,
                                borderColor: currentTheme.colors.border,
                                color: currentTheme.colors.text,
                              }
                        }
                      >
                        <p className="text-base font-semibold">{category}</p>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Category Demand Chart */}
                <CategoryDemand
                  restaurantId={restaurantId}
                  categoryName={selectedCategory}
                  hoursAhead={24}
                />
              </div>
            )}

            {/* Peak Hours Tab */}
            {activeTab === 'peaks' && (
              <PeakHours restaurantId={restaurantId} daysAhead={7} />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default DemandPage

// frontend/src/App.tsx

import React, { useEffect } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { DemandPage } from './pages/DemandPage'
import { useThemeStore, initializeTheme } from './stores/themeStore'
import { DEFAULT_RESTAURANT_ID } from './utils/constants'
import './App.css'

// Create a client for TanStack Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
})

/**
 * Main App Component
 */
function App() {
  const { currentTheme } = useThemeStore()

  // Initialize theme on app load
  useEffect(() => {
    initializeTheme()
  }, [])

  return (
    <QueryClientProvider client={queryClient}>
      <div
        className="min-h-screen"
        style={{
          backgroundColor: currentTheme.colors.background,
          color: currentTheme.colors.text,
        }}
      >
        {/* Main Content */}
        <DemandPage restaurantId={DEFAULT_RESTAURANT_ID} />
      </div>
    </QueryClientProvider>
  )
}

export default App

import React, { useState } from 'react'
import { useThemeStore } from '../../stores/themeStore'
import type { ThemeName } from '../../types/theme'

/**
 * Theme Selector Component
 * Allows users to switch between different themes
 */
export const ThemeSelector: React.FC = () => {
  const { themeName, setTheme, availableThemes, currentTheme } = useThemeStore()
  const [isOpen, setIsOpen] = useState(false)

  const themeDisplayNames: Record<ThemeName, { name: string; icon: string; description: string }> = {
    light: { name: 'Light', icon: '☀️', description: 'Bright and clean' },
    dark: { name: 'Dark', icon: '🌙', description: 'Easy on the eyes' },
    ocean: { name: 'Ocean', icon: '🌊', description: 'Cool and calm' },
    forest: { name: 'Forest', icon: '🌲', description: 'Natural and fresh' },
    sunset: { name: 'Sunset', icon: '🌅', description: 'Warm and vibrant' },
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all hover:shadow-md"
        style={{
          backgroundColor: currentTheme.colors.surface,
          color: currentTheme.colors.text,
          border: `2px solid ${currentTheme.colors.border}`,
        }}
      >
        <span className="text-xl">{themeDisplayNames[themeName].icon}</span>
        <span>{themeDisplayNames[themeName].name}</span>
        <svg
          className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown */}
          <div
            className="absolute right-0 mt-2 w-64 rounded-lg shadow-2xl z-20 overflow-hidden"
            style={{
              backgroundColor: currentTheme.colors.surface,
              border: `2px solid ${currentTheme.colors.border}`,
            }}
          >
            <div
              className="px-4 py-3 border-b"
              style={{
                borderColor: currentTheme.colors.border,
                backgroundColor: currentTheme.colors.backgroundSecondary,
              }}
            >
              <p className="text-sm font-semibold" style={{ color: currentTheme.colors.text }}>
                Choose Theme
              </p>
            </div>
            
            <div className="py-2">
              {availableThemes.map((theme) => (
                <button
                  key={theme}
                  onClick={() => {
                    setTheme(theme)
                    setIsOpen(false)
                  }}
                  className="w-full px-4 py-3 flex items-center gap-3 transition-all hover:shadow-sm"
                  style={{
                    backgroundColor: themeName === theme ? currentTheme.colors.primaryLight : 'transparent',
                    color: currentTheme.colors.text,
                  }}
                  onMouseEnter={(e) => {
                    if (themeName !== theme) {
                      e.currentTarget.style.backgroundColor = currentTheme.colors.surfaceHover
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (themeName !== theme) {
                      e.currentTarget.style.backgroundColor = 'transparent'
                    }
                  }}
                >
                  <span className="text-2xl">{themeDisplayNames[theme].icon}</span>
                  <div className="flex-1 text-left">
                    <p className="font-medium" style={{ color: currentTheme.colors.text }}>
                      {themeDisplayNames[theme].name}
                    </p>
                    <p className="text-xs" style={{ color: currentTheme.colors.textSecondary }}>
                      {themeDisplayNames[theme].description}
                    </p>
                  </div>
                  {themeName === theme && (
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      style={{ color: currentTheme.colors.primary }}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  )}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default ThemeSelector

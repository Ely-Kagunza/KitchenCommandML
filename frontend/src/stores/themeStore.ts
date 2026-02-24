import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Theme, ThemeName } from '../types/theme'
import { getTheme, getAvailableThemes } from '../themes'

interface ThemeStore {
    currentTheme: Theme
    themeName: ThemeName
    setTheme: (themeName: ThemeName) => void
    toggleTheme: () => void
    availableThemes: ThemeName[]
}

/**
 * Zustand store for theme management
 * Persists theme selection to localStorage
 */
export const useThemeStore = create<ThemeStore>()(
    persist(
        (set, get) => ({
            currentTheme: getTheme('light'),
            themeName: 'light',
            availableThemes: getAvailableThemes(),

            /**
             * Set theme by name
             */
            setTheme: (themeName: ThemeName) => {
                const theme = getTheme(themeName)
                set({
                    currentTheme: theme,
                    themeName: themeName,
                })
                // Apply theme to document
                applyThemeToDocument(theme)
            },

            /**
             * Toggle between light and dark themes
             */
            toggleTheme: () => {
                const { themeName } = get()
                const newTheme = themeName === 'light' ? 'dark' : 'light'
                get().setTheme(newTheme)
            },
        }),
        {
            name: 'theme-store',
            partialize: (state) => ({
                themeName: state.themeName,
            }),
        }
    )
)

/**
 * Apply theme colors to document CSS variables
 */
export const applyThemeToDocument = (theme: Theme) => {
    const root = document.documentElement
    const colors = theme.colors

    // Set CSS variables for all theme colors
    Object.entries(colors).forEach(([key, value]) => {
        root.style.setProperty(`--color-${key}`, value)
    })

    // Set data attributes for theme name
    root.setAttribute('data-theme', theme.name)

    // Set dark mode class if needed
    if (theme.isDark) {
        root.classList.add('dark')
    } else {
        root.classList.remove('dark')
    }
}

/**
 * Initialize theme on app load
 */
export const initializeTheme = () => {
    const { themeName, setTheme } = useThemeStore.getState()
    setTheme(themeName)
}
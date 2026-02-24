import type { Theme, ThemeName } from '../types/theme'
import { lightTheme } from './light'
import { darkTheme } from './dark'
import { oceanTheme } from './ocean'
import { forestTheme } from './forest'
import { sunsetTheme } from './sunset'

/**
 * All available themes
 */
export const themes: Record<ThemeName, Theme> = {
    light: lightTheme,
    dark: darkTheme,
    ocean: oceanTheme,
    forest: forestTheme,
    sunset: sunsetTheme,
}

/**
 * Get theme by name
 */
export const getTheme = (themeName: ThemeName): Theme => {
    return themes[themeName] || themes.light
}

/**
 * Get all available theme names
 */
export const getAvailableThemes = (): ThemeName[] => {
    return Object.keys(themes) as ThemeName[]
}

/**
 * Get theme display name (for UI)
 */
export const getThemeDisplayName = (themeName: ThemeName): string => {
    const displayNames: Record<ThemeName, string> = {
        light: 'Light',
        dark: 'Dark',
        ocean: 'Ocean',
        forest: 'Forest',
        sunset: 'Sunset',
    }
    return displayNames[themeName]
}

/**
 * Export all themes
 */
export { lightTheme, darkTheme, oceanTheme, forestTheme, sunsetTheme }
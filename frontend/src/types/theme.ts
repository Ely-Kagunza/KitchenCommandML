export type ThemeName = 'light' | 'dark' | 'ocean' | 'forest' | 'sunset'

export interface ThemeColors {
    // Primary colors
    primary: string
    primaryLight: string
    primaryDark: string

    // Secondary colors
    secondary: string
    secondaryLight: string
    secondaryDark: string

    // Accent colors
    accent: string
    accentLight: string
    accentDark: string

    // Background colors
    background: string
    backgroundSecondary: string
    surface: string
    surfaceHover: string

    // Text colors
    text: string
    textSecondary: string
    textTertiary: string
    textInverse: string

    // Border colors
    border: string
    borderLight: string
    borderDark: string

    // Status colors
    success: string
    successLight: string
    warning: string
    warningLight: string
    error: string
    errorLight: string
    info: string
    infoLight: string

    // Chart colors
    chart1: string
    chart2: string
    chart3: string
    chart4: string
    chart5: string
}

export interface Theme {
    name: ThemeName
    colors: ThemeColors
    isDark: boolean
}

export interface ThemeContextType {
    currentTheme: Theme
    themeName: ThemeName
    setTheme: (theme: ThemeName) => void
    availableThemes: Theme[]
}
import type { Theme } from '../types/theme'

export const darkTheme: Theme = {
  name: 'dark',
  isDark: true,
  colors: {
    // Primary colors
    primary: '#60A5FA',
    primaryLight: '#1E3A8A',
    primaryDark: '#93C5FD',
    
    // Secondary colors
    secondary: '#A78BFA',
    secondaryLight: '#3730A3',
    secondaryDark: '#DDD6FE',
    
    // Accent colors
    accent: '#F472B6',
    accentLight: '#831843',
    accentDark: '#FBCFE8',
    
    // Background colors
    background: '#0F172A',
    backgroundSecondary: '#1E293B',
    surface: '#1E293B',
    surfaceHover: '#334155',
    
    // Text colors
    text: '#F1F5F9',
    textSecondary: '#CBD5E1',
    textTertiary: '#94A3B8',
    textInverse: '#0F172A',
    
    // Border colors
    border: '#334155',
    borderLight: '#475569',
    borderDark: '#1E293B',
    
    // Status colors
    success: '#34D399',
    successLight: '#064E3B',
    warning: '#FBBF24',
    warningLight: '#78350F',
    error: '#F87171',
    errorLight: '#7F1D1D',
    info: '#22D3EE',
    infoLight: '#164E63',
    
    // Chart colors
    chart1: '#60A5FA',
    chart2: '#A78BFA',
    chart3: '#F472B6',
    chart4: '#FBBF24',
    chart5: '#34D399',
  },
}

import type { Theme } from '../types/theme'

export const oceanTheme: Theme = {
  name: 'ocean',
  isDark: false,
  colors: {
    // Primary colors
    primary: '#0369A1',
    primaryLight: '#CFF0F9',
    primaryDark: '#003D5C',
    
    // Secondary colors
    secondary: '#0891B2',
    secondaryLight: '#CFFAFE',
    secondaryDark: '#164E63',
    
    // Accent colors
    accent: '#06B6D4',
    accentLight: '#ECFDF5',
    accentDark: '#0E7490',
    
    // Background colors
    background: '#F0F9FF',
    backgroundSecondary: '#E0F2FE',
    surface: '#F8FAFC',
    surfaceHover: '#E2E8F0',
    
    // Text colors
    text: '#0C2340',
    textSecondary: '#475569',
    textTertiary: '#64748B',
    textInverse: '#FFFFFF',
    
    // Border colors
    border: '#BAE6FD',
    borderLight: '#E0F2FE',
    borderDark: '#7DD3FC',
    
    // Status colors
    success: '#0891B2',
    successLight: '#CFFAFE',
    warning: '#EA580C',
    warningLight: '#FFEDD5',
    error: '#DC2626',
    errorLight: '#FEE2E2',
    info: '#0284C7',
    infoLight: '#E0F2FE',
    
    // Chart colors
    chart1: '#0369A1',
    chart2: '#0891B2',
    chart3: '#06B6D4',
    chart4: '#EA580C',
    chart5: '#0284C7',
  },
}

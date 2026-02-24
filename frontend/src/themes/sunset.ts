import type { Theme } from '../types/theme'

export const sunsetTheme: Theme = {
  name: 'sunset',
  isDark: false,
  colors: {
    // Primary colors
    primary: '#EA580C',
    primaryLight: '#FFEDD5',
    primaryDark: '#92400E',
    
    // Secondary colors
    secondary: '#F97316',
    secondaryLight: '#FED7AA',
    secondaryDark: '#7C2D12',
    
    // Accent colors
    accent: '#DC2626',
    accentLight: '#FEE2E2',
    accentDark: '#7F1D1D',
    
    // Background colors
    background: '#FFFBEB',
    backgroundSecondary: '#FEF3C7',
    surface: '#FAFAF9',
    surfaceHover: '#F5F5F4',
    
    // Text colors
    text: '#78350F',
    textSecondary: '#B45309',
    textTertiary: '#D97706',
    textInverse: '#FFFFFF',
    
    // Border colors
    border: '#FED7AA',
    borderLight: '#FFEDD5',
    borderDark: '#FDBA74',
    
    // Status colors
    success: '#059669',
    successLight: '#D1FAE5',
    warning: '#F59E0B',
    warningLight: '#FEF3C7',
    error: '#DC2626',
    errorLight: '#FEE2E2',
    info: '#0891B2',
    infoLight: '#CFFAFE',
    
    // Chart colors
    chart1: '#EA580C',
    chart2: '#F97316',
    chart3: '#DC2626',
    chart4: '#F59E0B',
    chart5: '#059669',
  },
}

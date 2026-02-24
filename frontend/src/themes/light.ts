import type { Theme } from '../types/theme'

export const lightTheme: Theme = {
  name: 'light',
  isDark: false,
  colors: {
    // Primary colors
    primary: '#3B82F6',
    primaryLight: '#DBEAFE',
    primaryDark: '#1E40AF',
    
    // Secondary colors
    secondary: '#8B5CF6',
    secondaryLight: '#EDE9FE',
    secondaryDark: '#5B21B6',
    
    // Accent colors
    accent: '#EC4899',
    accentLight: '#FCE7F3',
    accentDark: '#BE185D',
    
    // Background colors
    background: '#FFFFFF',
    backgroundSecondary: '#F9FAFB',
    surface: '#F3F4F6',
    surfaceHover: '#E5E7EB',
    
    // Text colors
    text: '#111827',
    textSecondary: '#6B7280',
    textTertiary: '#9CA3AF',
    textInverse: '#FFFFFF',
    
    // Border colors
    border: '#E5E7EB',
    borderLight: '#F3F4F6',
    borderDark: '#D1D5DB',
    
    // Status colors
    success: '#10B981',
    successLight: '#D1FAE5',
    warning: '#F59E0B',
    warningLight: '#FEF3C7',
    error: '#EF4444',
    errorLight: '#FEE2E2',
    info: '#06B6D4',
    infoLight: '#CFFAFE',
    
    // Chart colors
    chart1: '#3B82F6',
    chart2: '#8B5CF6',
    chart3: '#EC4899',
    chart4: '#F59E0B',
    chart5: '#10B981',
  },
}

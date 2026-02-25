import { describe, it, expect, beforeEach } from 'vitest'
import { useThemeStore } from '../themeStore'

describe('ThemeStore', () => {
  beforeEach(() => {
    // Reset store before each test
    useThemeStore.setState({ themeName: 'light' })
  })

  it('should have default theme as light', () => {
    const { themeName } = useThemeStore.getState()
    expect(themeName).toBe('light')
  })

  it('should change theme', () => {
    const { setTheme } = useThemeStore.getState()
    
    setTheme('dark')
    expect(useThemeStore.getState().themeName).toBe('dark')
    
    setTheme('ocean')
    expect(useThemeStore.getState().themeName).toBe('ocean')
  })

  it('should have currentTheme object', () => {
    const { currentTheme } = useThemeStore.getState()
    
    expect(currentTheme).toBeDefined()
    expect(currentTheme.name).toBeDefined()
    expect(currentTheme.colors).toBeDefined()
    expect(currentTheme.colors.primary).toBeDefined()
    expect(currentTheme.colors.background).toBeDefined()
  })

  it('should update currentTheme when theme changes', () => {
    const { setTheme } = useThemeStore.getState()
    
    setTheme('dark')
    const darkTheme = useThemeStore.getState().currentTheme
    expect(darkTheme.name).toBe('dark')
    
    setTheme('light')
    const lightTheme = useThemeStore.getState().currentTheme
    expect(lightTheme.name).toBe('light')
    
    expect(darkTheme.colors.background).not.toBe(lightTheme.colors.background)
  })
})

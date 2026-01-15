import type { ThemeContextType } from '@/contexts/theme'
import { use } from 'react'
import { ThemeContext } from '@/contexts/theme'

export function useTheme(): ThemeContextType {
  const context = use(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

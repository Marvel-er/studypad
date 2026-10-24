'use client'

import { useEffect, useState, createContext, useContext } from 'react'

type Theme = 'light' | 'dark'

interface ThemeContextValue {
  theme: Theme
  toggleTheme: () => void
  setTheme: (t: Theme) => void
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined)

const STORAGE_KEY = 'ielts-vocab-theme'

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>('light')
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    // Read from localStorage or system preference
    const stored = localStorage.getItem(STORAGE_KEY) as Theme | null
    const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    const initial: Theme = stored ?? (systemDark ? 'dark' : 'light')
    // defer to avoid synchronous setState in effect
    Promise.resolve().then(() => {
      setThemeState(initial)
      setMounted(true)
    })
  }, [])

  useEffect(() => {
    if (!mounted) return
    const root = document.documentElement
    if (theme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
    localStorage.setItem(STORAGE_KEY, theme)
  }, [theme, mounted])

  const setTheme = (t: Theme) => setThemeState(t)
  const toggleTheme = () => setThemeState((t) => (t === 'dark' ? 'light' : 'dark'))

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const ctx = useContext(ThemeContext)
  if (!ctx) {
    // Fallback for SSR / outside provider
    return { theme: 'light' as Theme, toggleTheme: () => {}, setTheme: () => {} }
  }
  return ctx
}

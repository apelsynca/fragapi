import { useEffect, useState } from 'react'
import { SunIcon, MoonIcon, MonitorIcon } from 'lucide-react'
import { DropdownMenuItem } from './ui/dropdown-menu'

type ThemeMode = 'light' | 'dark' | 'auto'

function getInitialMode(): ThemeMode {
  if (typeof window === 'undefined') {
    return 'auto'
  }

  const stored = window.localStorage.getItem('theme')
  if (stored === 'light' || stored === 'dark' || stored === 'auto') {
    return stored
  }

  return 'auto'
}

function applyThemeMode(mode: ThemeMode) {
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  const resolved = mode === 'auto' ? (prefersDark ? 'dark' : 'light') : mode

  document.documentElement.classList.remove('light', 'dark')
  document.documentElement.classList.add(resolved)

  if (mode === 'auto') {
    document.documentElement.removeAttribute('data-theme')
  } else {
    document.documentElement.setAttribute('data-theme', mode)
  }

  document.documentElement.style.colorScheme = resolved
}

export default function useThemeToggle() {
  const [theme, setTheme] = useState<ThemeMode>('auto')

  useEffect(() => {
    const initialMode = getInitialMode()
    setTheme(initialMode)
    applyThemeMode(initialMode)
  }, [])

  useEffect(() => {
    if (theme !== 'auto') {
      return
    }

    const media = window.matchMedia('(prefers-color-scheme: dark)')
    const onChange = () => applyThemeMode('auto')

    media.addEventListener('change', onChange)
    return () => {
      media.removeEventListener('change', onChange)
    }
  }, [theme])

  function toggleMode() {
    const nextMode: ThemeMode =
      theme === 'light' ? 'dark' : theme === 'dark' ? 'auto' : 'light'
    setTheme(nextMode)
    applyThemeMode(nextMode)
    window.localStorage.setItem('theme', nextMode)
  }

  const label =
    theme === 'auto'
      ? 'Theme mode: auto (system). Click to switch to light mode.'
      : `Theme mode: ${theme}. Click to switch mode.`

  return { theme, toggleMode, label }
}

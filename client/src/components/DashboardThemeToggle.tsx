import { MonitorIcon, MoonIcon, SunIcon } from 'lucide-react'
import { DropdownMenuItem } from './ui/dropdown-menu.tsx'
import useThemeToggle from './useThemeToggle.ts'
import { useTranslation } from 'react-i18next'

export default function DashboardThemeToggle() {
  const { theme, toggleTheme, label } = useThemeToggle()
  const { t } = useTranslation()

  return (
    <DropdownMenuItem onClick={toggleTheme} aria-label={label} title={label}>
      {theme === 'auto' ? (
        <>
          <MonitorIcon /> {t('sidebar.theme_system')}
        </>
      ) : theme === 'dark' ? (
        <>
          <MoonIcon /> {t('sidebar.theme_dark')}
        </>
      ) : (
        <>
          <SunIcon /> {t('sidebar.theme_light')}
        </>
      )}
    </DropdownMenuItem>
  )
}

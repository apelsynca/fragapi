import { MonitorIcon, MoonIcon, SunIcon } from 'lucide-react'
import { DropdownMenuItem } from '~/components/ui/dropdown-menu.tsx'
import useThemeToggle from '~/hooks/useThemeToggle.ts'

export default function DashboardThemeToggle() {
  const { theme, toggleTheme, label } = useThemeToggle()

  return (
    <DropdownMenuItem onClick={toggleTheme} aria-label={label} title={label}>
      {theme === 'auto' ? (
        <>
          <MonitorIcon /> {'sidebar.theme_system'}
        </>
      ) : theme === 'dark' ? (
        <>
          <MoonIcon /> {'sidebar.theme_dark'}
        </>
      ) : (
        <>
          <SunIcon /> {'sidebar.theme_light'}
        </>
      )}
    </DropdownMenuItem>
  )
}

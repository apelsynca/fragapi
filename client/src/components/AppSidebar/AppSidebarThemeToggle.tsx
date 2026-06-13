import { MonitorIcon, MoonIcon, SunIcon } from 'lucide-react'
import { DropdownMenuItem } from '~/components/ui/dropdown-menu.tsx'
import useThemeToggle from '~/hooks/useThemeToggle.ts'
import { m } from '~/paraglide/messages'

export default function AppSidebarThemeToggle() {
  const { theme, toggleTheme, label } = useThemeToggle()

  return (
    <DropdownMenuItem onClick={toggleTheme} aria-label={label} title={label}>
      {theme === 'auto' ? (
        <>
          <MonitorIcon /> {m.theme_system()}
        </>
      ) : theme === 'dark' ? (
        <>
          <MoonIcon /> {m.theme_dark()}
        </>
      ) : (
        <>
          <SunIcon /> {m.theme_light()}
        </>
      )}
    </DropdownMenuItem>
  )
}

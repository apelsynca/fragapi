import { useThemeToggle } from './useThemeToggle.ts'

export default function DashboardThemeToggle() {
  const { mode, toggleMode, label } = useThemeToggle()

  return (
    <DropdownMenuItem onClick={toggleMode} aria-label={label} title={label}>
      {mode === 'auto' ? (
        <>
          <MonitorIcon /> {t('sidebar.theme_system')}
        </>
      ) : mode === 'dark' ? (
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

import { LanguagesIcon, MoonIcon, SunIcon } from 'lucide-react'
import { getLocale, setLocale } from '~/paraglide/runtime'
import { Button } from '../ui/button'
import { useTheme } from '../theme-provider'

const HeaderThemeToggle = () => {
  const { setTheme } = useTheme()

  return (
    <Button variant="outline" size="icon-lg" onClick={() => setTheme('dark')}>
      <MoonIcon className="h-[1.2rem] w-[1.2rem] scale-100 rotate-0 transition-all dark:scale-0 dark:-rotate-90" />
      <SunIcon className="absolute h-[1.2rem] w-[1.2rem] scale-0 rotate-90 transition-all dark:scale-100 dark:rotate-0" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  )
}

const HeaderLanguageToggle = () => {
  const locale = getLocale()

  return (
    <Button
      variant="outline"
      size="icon-lg"
      onClick={() => {
        setLocale(locale === 'ru' ? 'en' : 'ru')
      }}
    >
      <LanguagesIcon />
    </Button>
  )
}

export default function Header() {
  return (
    <div className="py-4">
      <div className="flex gap-1">
        <HeaderThemeToggle />
        <HeaderLanguageToggle />
      </div>
    </div>
  )
}

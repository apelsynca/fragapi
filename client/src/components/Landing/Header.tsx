import { LanguagesIcon } from 'lucide-react'
import { LoginButton } from './LandingActions'
import { getLocale, setLocale } from '#/paraglide/runtime'
import { Button } from '#/components/ui/button'
import { siteConfig } from '#/config'
import { m } from '#/paraglide/messages'

const HeaderLanguageToggle = () => {
  const locale = getLocale()

  return (
    <Button
      variant="secondary"
      size="icon"
      aria-label={locale === 'ru' ? 'English' : 'Русский'}
      onClick={() => {
        setLocale(locale === 'ru' ? 'en' : 'ru')
      }}
    >
      <LanguagesIcon />
    </Button>
  )
}

export default function Header({ toPanel = false }: { toPanel?: boolean }) {
  return (
    <header className="w-full px-4">
      <div className="mx-auto flex max-w-280 items-center justify-between pt-6">
        <span className="text-xl font-semibold tracking-[-0.01em]">
          FragAPI
        </span>
        <nav className="flex items-center gap-2">
          <div className="text-muted-foreground hidden gap-7 pr-5 text-sm font-medium sm:flex">
            <a
              href={siteConfig.docs}
              className="hover:text-foreground transition-colors"
            >
              {m.land_docs()}
            </a>
            <a
              href={siteConfig.github}
              className="hover:text-foreground transition-colors"
            >
              GitHub
            </a>
          </div>
          <HeaderLanguageToggle />
          <LoginButton toPanel={toPanel} />
        </nav>
      </div>
    </header>
  )
}

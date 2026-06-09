import { Link } from '@tanstack/react-router'
import { Button } from './ui/button'
import { ExternalLink } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import ThemeToggle from './ThemeToggle'
import { useThemeToggle } from './useThemeToggle.ts'

export default function Landing({ toPanel = false }: { toPanel?: boolean }) {
  const { t } = useTranslation()
  const { mode, toggleMode, label } = useThemeToggle()

  return (
    <main className="flex min-h-screen items-center justify-center">
      <header>
        <ThemeToggle />
      </header>

      <div className="flex flex-col gap-6 max-w-xl pb-20">
        <div className="flex flex-col gap-2">
          <h1 className="text-4xl font-bold text-center">{t('land.cta')}</h1>
          <p className="text-lg text-center text-gray-100">{t('land.desc')}</p>
        </div>

        <div className="flex justify-center gap-1">
          {toPanel ? (
            <Button asChild>
              <Link to="/dashboard">{t('land.go_to_panel')}</Link>
            </Button>
          ) : (
            <Button asChild>
              <a
                href={`https://t.me/${import.meta.env.VITE_BOT_USERNAME}?start=login`}
              >
                {t('land.bot_login')}
              </a>
            </Button>
          )}
          <Button asChild variant="secondary">
            <a href="https://docs.fragapi.com">
              {t('land.learn_more')} <ExternalLink />
            </a>
          </Button>
        </div>
      </div>
    </main>
  )
}

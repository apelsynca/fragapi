import { useTranslation } from 'react-i18next'
import Hero from './Hero'

export default function Landing({ toPanel = false }: { toPanel?: boolean }) {
  const { t } = useTranslation()

  // const toggleLanguage = () => {
  //   const next = i18n.language === 'en' ? 'ru' : 'en'
  //   i18n.changeLanguage(next)
  // }

  return (
    <main className="flex flex-col min-h-screen items-center gap-8 md:justify-between">
      <Hero
        title={t('land.title')}
        description={t('land.description')}
        className="w-full"
        toPanel={toPanel}
      />
    </main>
  )
}

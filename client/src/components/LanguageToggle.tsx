import { LanguagesIcon } from 'lucide-react'
import { DropdownMenuItem } from './ui/dropdown-menu'
import { useTranslation } from 'react-i18next'

export default function LanguageToggle() {
  const { i18n } = useTranslation()

  const toggleLanguage = () => {
    const next = i18n.language === 'en' ? 'ru' : 'en'
    i18n.changeLanguage(next)
  }

  return (
    <DropdownMenuItem onClick={toggleLanguage}>
      <LanguagesIcon />{' '}
      {i18n.language === 'en' ? 'Lang: English' : 'Язык: Русский'}
    </DropdownMenuItem>
  )
}

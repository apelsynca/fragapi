import i18next from 'i18next'
import { initReactI18next } from 'react-i18next'
import ru from './locales/ru.json'
import en from './locales/en.json'

export function createI18nInstance(lng: string) {
  const i18n = i18next.createInstance()
  i18n.use(initReactI18next).init({
    resources: {
      en: { translation: en },
      ru: { translation: ru },
    },
    lng,
    fallbackLng: 'ru',
    interpolation: { escapeValue: false },
  })

  return i18n
}

import i18n from 'i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import { initReactI18next } from 'react-i18next'
import en from '~/locales/en.json'
import ru from '~/locales/ru.json'

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      ru: { translation: ru },
    },
    fallbackLng: 'ru',
    supportedLngs: ['en', 'ru'],
    nonExplicitSupportedLngs: false,
    detection: {
      order: ['cookie', 'localStorage', 'navigator'],
      caches: ['cookie'], // persist in cookie for SSR
      cookieMinutes: 10080, // 7 days
    },
  })

export default i18n

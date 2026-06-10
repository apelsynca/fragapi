import { createIsomorphicFn } from '@tanstack/react-start'
import { getCookie, getRequestHeader } from '@tanstack/react-start/server'
import acceptLanguage from 'accept-language'
import i18n from './i18n-config'

acceptLanguage.languages(['ru'])

export const getLocale = createIsomorphicFn()
  .client(() => {
    return i18n.language
  })
  .server(() => {
    // 1. Check for a cookie first
    const cookieLocale = getCookie('i18next')
    if (cookieLocale) return cookieLocale

    // 2. Fall back to the Accept-Language header
    const header = getRequestHeader('accept-language')
    const parsed = acceptLanguage.get(header)
    const locale = parsed || 'ru' // default to Russian

    // Synchronise the i18next instance on the server
    i18n.changeLanguage(locale)
    return locale
  })

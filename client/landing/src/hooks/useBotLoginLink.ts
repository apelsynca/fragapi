import { useEffect, useState } from 'react'
import { getBotLoginLink } from '../../../shared/signup-attribution'
import { siteConfig } from '#/config'

export function useBotLoginLink() {
  const [href, setHref] = useState(
    `https://t.me/${siteConfig.botUsername}?start=login`,
  )
  useEffect(() => {
    setHref(
      getBotLoginLink(
        siteConfig.botUsername,
        import.meta.env.VITE_API_URL || 'https://api.fragapi.com/v1',
        siteConfig.docs,
        window.location.hostname,
      ),
    )
  }, [])
  return href
}

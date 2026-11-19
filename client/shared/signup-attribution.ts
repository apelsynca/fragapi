const STORAGE_KEY = 'fragapi.signup-attribution.v1'
const TTL_MS = 30 * 24 * 60 * 60 * 1000

interface Attribution {
  source?: string
  medium?: string
  campaign?: string
  referrer?: string
}

interface SavedAttribution {
  expiresAt: number
  data: Attribution
}

// Also retain first touch when browser storage is blocked.
let memory: SavedAttribution | undefined

function clean(value: string | null): string | undefined {
  return (
    value
      ?.replace(/[\x00-\x1f\x7f]/g, '')
      .trim()
      .slice(0, 128) || undefined
  )
}

function capture(apiUrl: string, docsUrl: string): Attribution {
  const now = Date.now()
  if (memory && memory.expiresAt > now) return memory.data
  try {
    const saved: SavedAttribution = JSON.parse(
      window.localStorage.getItem(STORAGE_KEY) || 'null',
    )
    if (
      saved &&
      Number.isFinite(saved.expiresAt) &&
      saved.expiresAt > now &&
      saved.expiresAt <= now + TTL_MS &&
      saved.data &&
      Object.entries(saved.data).every(
        ([key, value]) =>
          ['source', 'medium', 'campaign', 'referrer'].includes(key) &&
          typeof value === 'string' &&
          value.length <= (key === 'referrer' ? 253 : 128) &&
          (key === 'referrer'
            ? /^[a-zA-Z0-9._:-]+$/.test(value)
            : !/[\x00-\x1f\x7f]/.test(value)),
      )
    ) {
      memory = saved
      return saved.data
    }
  } catch {
    // Invalid or unavailable storage must not prevent login.
  }

  const params = new URLSearchParams(window.location.search)
  const data: Attribution = {}
  for (const key of ['source', 'medium', 'campaign'] as const) {
    const value = clean(params.get(`utm_${key}`))
    if (value) data[key] = value
  }
  try {
    const referrer = new URL(document.referrer)
    const ownHosts = [
      window.location.hostname,
      new URL(apiUrl, window.location.origin).hostname,
      new URL(docsUrl).hostname,
    ]
    const internal = ownHosts.some(
      (host) =>
        referrer.hostname === host ||
        referrer.hostname.endsWith(`.${host}`) ||
        host.endsWith(`.${referrer.hostname}`),
    )
    if (
      ['http:', 'https:'].includes(referrer.protocol) &&
      !internal &&
      referrer.hostname
    ) {
      data.referrer = referrer.hostname
      if (!data.source) data.source = referrer.hostname.slice(0, 128)
    }
  } catch {
    // Referrers can be absent or suppressed by the browser.
  }

  memory = { expiresAt: now + TTL_MS, data }
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(memory))
  } catch {
    // Keep the in-memory first touch if storage is blocked.
  }
  return data
}

export function getBotLoginLink(
  botUsername: string,
  apiUrl: string,
  docsUrl: string,
  defaultMedium?: string,
): string {
  const fallback = `https://t.me/${botUsername}?start=login`
  if (typeof window === 'undefined') return fallback
  const data = { ...capture(apiUrl, docsUrl) }
  const medium = data.medium || clean(defaultMedium ?? null)
  if (medium) data.medium = medium
  if (Object.keys(data).length === 0) return fallback
  try {
    const url = new URL(
      `${apiUrl.replace(/\/$/, '')}/attribution/start`,
      window.location.origin,
    )
    for (const [key, value] of Object.entries(data))
      url.searchParams.set(key, value)
    return url.href
  } catch {
    return fallback
  }
}

import { beforeEach, describe, expect, it, vi } from 'vitest'

const API = 'https://api.fragapi.com/v1'
const DOCS = 'https://docs.fragapi.com'
const KEY = 'fragapi.signup-attribution.v1'
const TTL = 30 * 24 * 60 * 60 * 1000

async function loginLink(defaultMedium?: string) {
  const { getBotLoginLink } = await import('../../../shared/signup-attribution')
  return getBotLoginLink('frag_api_bot', API, DOCS, defaultMedium)
}

beforeEach(() => {
  vi.restoreAllMocks()
  vi.unstubAllGlobals()
  vi.resetModules()
  window.localStorage.clear()
  window.history.replaceState({}, '', '/')
  Object.defineProperty(document, 'referrer', { value: '', configurable: true })
})

describe('signup attribution', () => {
  it('passes UTMs to the server redirect without a network request', async () => {
    window.history.replaceState(
      {},
      '',
      '/?utm_source=telegram&utm_medium=channel&utm_campaign=launch',
    )
    const url = new URL(await loginLink())
    expect(url.origin + url.pathname).toBe(`${API}/attribution/start`)
    expect(Object.fromEntries(url.searchParams)).toEqual({
      source: 'telegram',
      medium: 'channel',
      campaign: 'launch',
    })
  })

  it.each([
    ['/', { medium: 'landing.example' }],
    [
      '/?utm_source=telegram',
      { source: 'telegram', medium: 'landing.example' },
    ],
    [
      '/?utm_source=telegram&utm_medium=channel',
      { source: 'telegram', medium: 'channel' },
    ],
  ])('applies the landing medium default for %s', async (path, expected) => {
    window.history.replaceState({}, '', path)
    const url = new URL(await loginLink('landing.example'))
    expect(Object.fromEntries(url.searchParams)).toEqual(expected)
  })

  it('preserves first touch across subsequent visits and page reloads', async () => {
    window.history.replaceState({}, '', '/?utm_source=first')
    const first = await loginLink()
    window.history.replaceState({}, '', '/?utm_source=second')
    expect(await loginLink()).toBe(first)
    vi.resetModules()
    expect(await loginLink()).toBe(first)
  })

  it('captures a fresh visit after 30 days', async () => {
    window.localStorage.setItem(
      KEY,
      JSON.stringify({ expiresAt: Date.now() - 1, data: { source: 'old' } }),
    )
    window.history.replaceState({}, '', '/?utm_source=new')
    expect(new URL(await loginLink()).searchParams.get('source')).toBe('new')
    expect(
      JSON.parse(window.localStorage.getItem(KEY)!).expiresAt,
    ).toBeGreaterThan(Date.now() + TTL - 1000)
  })

  it('uses only an external referrer hostname, without its path or query', async () => {
    Object.defineProperty(document, 'referrer', {
      value: 'https://search.example/private?q=secret',
      configurable: true,
    })
    const params = new URL(await loginLink()).searchParams
    expect(Object.fromEntries(params)).toEqual({
      source: 'search.example',
      referrer: 'search.example',
    })
  })

  it('prefers an explicit UTM source over the referrer', async () => {
    window.history.replaceState({}, '', '/?utm_source=partner')
    Object.defineProperty(document, 'referrer', {
      value: 'https://search.example/',
      configurable: true,
    })
    expect(new URL(await loginLink()).searchParams.get('source')).toBe(
      'partner',
    )
  })

  it('ignores internal navigation and uses the plain login link', async () => {
    Object.defineProperty(document, 'referrer', {
      value: `${DOCS}/guide`,
      configurable: true,
    })
    expect(await loginLink()).toBe('https://t.me/frag_api_bot?start=login')
  })

  it('retains an unattributed first visit', async () => {
    const first = await loginLink()
    window.history.replaceState({}, '', '/?utm_source=later')
    vi.resetModules()
    expect(await loginLink()).toBe(first)
  })

  it('works when browser storage is blocked', async () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('blocked')
    })
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('blocked')
    })
    window.history.replaceState({}, '', '/?utm_source=first')
    const first = await loginLink()
    window.history.replaceState({}, '', '/?utm_source=second')
    expect(await loginLink()).toBe(first)
    expect(new URL(first).searchParams.get('source')).toBe('first')
  })

  it('ignores corrupt storage and bounds incoming values', async () => {
    window.localStorage.setItem(KEY, 'invalid json')
    window.history.replaceState(
      {},
      '',
      `/?utm_source=${'a'.repeat(200)}&utm_campaign=hello%0Aworld`,
    )
    const params = new URL(await loginLink()).searchParams
    expect(params.get('source')).toHaveLength(128)
    expect(params.get('campaign')).toBe('helloworld')
  })

  it('is safe during server rendering', async () => {
    vi.stubGlobal('window', undefined)
    expect(await loginLink()).toBe('https://t.me/frag_api_bot?start=login')
  })

  it('supports an API served through a same-origin proxy', async () => {
    window.history.replaceState({}, '', '/?utm_source=partner')
    const { getBotLoginLink } =
      await import('../../../shared/signup-attribution')
    const url = new URL(getBotLoginLink('frag_api_bot', '/v1', DOCS))
    expect(url.origin).toBe(window.location.origin)
    expect(url.pathname).toBe('/v1/attribution/start')
    expect(url.searchParams.get('source')).toBe('partner')
  })
})

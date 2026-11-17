import { createServerFn } from '@tanstack/react-start'
import { apiRequest } from '#/server-api/request'
import type { StatsTotals } from '#/server-api/models/stats'

const CACHE_TIME_MS = 30_000
// The landing must not wait for a slow backend.
const BACKEND_TIMEOUT_MS = 3_000

let lastTotals: StatsTotals | null = null
let lastAttemptAt = 0
let pending: Promise<StatsTotals | null> | null = null

const requestTotals = async () => {
  try {
    lastTotals = await Promise.race([
      apiRequest<StatsTotals>({ method: 'GET', endpoint: '/stats/totals' }),
      new Promise<never>((_, reject) =>
        setTimeout(() => reject(new Error('timeout')), BACKEND_TIMEOUT_MS),
      ),
    ])
  } catch {
    // Keep showing the last known totals.
  }

  return lastTotals
}

// Public: every visitor shares one cached copy, so the backend sees one
// request per CACHE_TIME_MS however many people open the landing.
export const fetchStatsTotals = createServerFn().handler(async () => {
  if (pending) return pending

  if (Date.now() - lastAttemptAt < CACHE_TIME_MS) return lastTotals

  lastAttemptAt = Date.now()
  pending = requestTotals().finally(() => {
    pending = null
  })

  return pending
})

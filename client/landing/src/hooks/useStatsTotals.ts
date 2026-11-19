import { useEffect, useState } from 'react'

interface StatsTotals {
  starsTotal: number
  premiumMonthsTotal: number
}

export function useStatsTotals() {
  const [data, setData] = useState<StatsTotals>()

  useEffect(() => {
    const controller = new AbortController()
    const endpoint = (
      import.meta.env.VITE_API_URL || 'https://api.fragapi.com/v1'
    ).replace(/\/$/, '')

    const refresh = async () => {
      try {
        const response = await fetch(`${endpoint}/stats/totals`, {
          signal: AbortSignal.any([
            controller.signal,
            AbortSignal.timeout(3_000),
          ]),
        })
        if (!response.ok) return

        const totals = await response.json()
        if (
          !controller.signal.aborted &&
          typeof totals?.starsTotal === 'number' &&
          typeof totals?.premiumMonthsTotal === 'number'
        ) {
          setData(totals)
        }
      } catch {
        // Keep the last known totals when the API is unavailable.
      }
    }

    void refresh()
    const timer = setInterval(() => void refresh(), 30_000)
    return () => {
      controller.abort()
      clearInterval(timer)
    }
  }, [])

  return { data }
}

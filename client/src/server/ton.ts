import { createServerFn } from '@tanstack/react-start'
import { apiRequest } from '~/server/request'
import { verifySession } from '~/lib/auth'

interface TonRate {
  tonRate: number
}

// in USD
export const fetchTonRate = createServerFn().handler(async () => {
  const token = await verifySession()

  const data = await apiRequest<TonRate>({
    method: 'GET',
    endpoint: '/ton/rate',
    token,
  })

  return data.tonRate
})

import { createServerFn } from '@tanstack/react-start'
import { apiRequest } from './request'
import { verifySession } from './auth'

// in USD
export const fetchTonRate = createServerFn().handler(async () => {
  const token = await verifySession()

  const answer = await apiRequest({
    method: 'GET',
    endpoint: '/panel/fragment/rate',
    token,
  })

  return answer['tonRate']
})

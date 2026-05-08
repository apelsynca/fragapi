import { createServerFn } from '@tanstack/react-start'
import { apiRequest } from './request'

// in USD
export const fetchTonRate = createServerFn().handler(async () => {
  const answer = await apiRequest({
    data: {
      method: 'GET',
      endpoint: '/panel/fragment/rate',
    },
  })

  return answer['tonRate']
})

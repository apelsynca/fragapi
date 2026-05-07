import { createServerFn } from '@tanstack/react-start'
import { apiRequest } from './request'
import { queryOptions } from '@tanstack/react-query'

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

export const tonRateQueryOptions = () =>
  queryOptions({
    queryKey: ['rate'],
    queryFn: () => fetchTonRate(),
    staleTime: 300 * 1000,
    refetchInterval: 300 * 1000,
  })

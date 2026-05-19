import { queryOptions } from '@tanstack/react-query'
import { fetchMe } from '~/server/user'
import { fetchTonRate } from '~/server/ton'

export const userMeQueryOptions = () =>
  queryOptions({
    queryKey: ['users', 'me'],
    queryFn: () => fetchMe(),
  })

export const tonRateQueryOptions = () =>
  queryOptions({
    queryKey: ['rate'],
    queryFn: () => fetchTonRate(),
  })

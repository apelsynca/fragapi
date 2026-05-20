import { queryOptions } from '@tanstack/react-query'
import { fetchMe } from '~/server/user'
import { fetchTonRate } from '~/server/ton'
import {
  fetchTransactionsPage,
  fetchTransactionsStats,
} from '~/server/transactions'

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

export const transactionsListQueryOptions = (page: number) =>
  queryOptions({
    queryKey: ['transactions', 'list', page],
    queryFn: () =>
      fetchTransactionsPage({ data: { page, sorting: '-created_at' } }),
  })

export const transactionsStatsQueryOptions = () =>
  queryOptions({
    queryKey: ['transactions', 'stats'],
    queryFn: () => fetchTransactionsStats(),
  })

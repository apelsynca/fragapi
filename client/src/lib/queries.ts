import { queryOptions } from '@tanstack/react-query'
import { fetchMe } from './user'
import { fetchTransactionsChart, fetchTransactionStats } from './transactions'
import { fetchTonRate } from './fragment'

export const userMeQueryOptions = () =>
  queryOptions({
    queryKey: ['users', 'me'],
    queryFn: () => fetchMe(),
  })

export const transactionStatsOptions = () =>
  queryOptions({
    queryKey: ['transactions', 'stats'],
    queryFn: () => fetchTransactionStats(),
  })

export const transactionChartOptions = () =>
  queryOptions({
    queryKey: ['transactions', 'chart'],
    queryFn: () => fetchTransactionsChart(),
  })

export const tonRateQueryOptions = () =>
  queryOptions({
    queryKey: ['rate'],
    queryFn: () => fetchTonRate(),
    staleTime: 300 * 1000,
    refetchInterval: 300 * 1000,
  })

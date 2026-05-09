import { queryOptions } from '@tanstack/react-query'
import { fetchMe } from './user'
import { fetchTonRate } from './fragment'
import { fetchATransactionsChart, fetchATransactionStats } from './different'

export const userMeQueryOptions = () =>
  queryOptions({
    queryKey: ['users', 'me'],
    queryFn: () => fetchMe(),
  })

export const transactionStatsOptions = () =>
  queryOptions({
    queryKey: ['transactions', 'stats'],
    queryFn: () => fetchATransactionStats(),
  })

export const transactionChartOptions = () =>
  queryOptions({
    queryKey: ['transactions', 'chart'],
    queryFn: () => fetchATransactionsChart(),
  })

export const tonRateQueryOptions = () =>
  queryOptions({
    queryKey: ['rate'],
    queryFn: () => fetchTonRate(),
  })

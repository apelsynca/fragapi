import { createServerFn } from '@tanstack/react-start'
import type { TransactionStats, TransChartPoint } from './models/transactions'
import { apiRequest } from './request'
import { queryOptions } from '@tanstack/react-query'

const fetchTransactionStats = createServerFn().handler(async () => {
  return (await apiRequest({
    data: {
      method: 'GET',
      endpoint: '/transactions/stats',
    },
  })) as TransactionStats
})

const fetchTransactionsChart = createServerFn().handler(async () => {
  return (await apiRequest({
    data: {
      method: 'GET',
      endpoint: '/transactions/chart',
    },
  })) as TransChartPoint[]
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

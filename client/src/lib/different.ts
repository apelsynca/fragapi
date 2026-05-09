import { createServerFn } from '@tanstack/react-start'
import type { TransactionStats, TransChartPoint } from './models/transactions'
import { apiRequest } from './request'

export const fetchATransactionStats = createServerFn().handler(async () => {
  return (await apiRequest({
    data: {
      method: 'GET',
      endpoint: '/transactions/stats',
    },
  })) as TransactionStats
})

export const fetchATransactionsChart = createServerFn().handler(async () => {
  return (await apiRequest({
    data: {
      method: 'GET',
      endpoint: '/transactions/chart',
    },
  })) as TransChartPoint[]
})

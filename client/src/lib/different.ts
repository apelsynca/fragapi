import { createServerFn } from '@tanstack/react-start'
import type { TransactionStats, TransChartPoint } from './models/transactions'
import { apiRequest } from './request'
import { verifySession } from './auth'

export const fetchATransactionStats = createServerFn().handler(async () => {
  const token = await verifySession()

  const data = await apiRequest({
    method: 'GET',
    endpoint: '/transactions/stats',
    token,
  })

  return data as TransactionStats
})

export const fetchATransactionsChart = createServerFn().handler(async () => {
  const token = await verifySession()

  const data = await apiRequest({
    method: 'GET',
    endpoint: '/transactions/chart',
    token,
  })

  return data as TransChartPoint[]
})

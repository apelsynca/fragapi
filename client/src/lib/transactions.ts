import { createServerFn } from '@tanstack/react-start'
import type {
  Transaction,
  TransactionStats,
  TransChartPoint,
} from './models/transactions'
import type { ListResource } from './models/misc'
import { apiRequest } from './request'
import { verifySession } from './auth'

export const fetchTransactionStats = createServerFn().handler(async () => {
  const token = await verifySession()

  const data = await apiRequest({
    method: 'GET',
    endpoint: '/transactions/stats',
    token,
  })

  return data as TransactionStats
})

export const fetchTransactionsChart = createServerFn().handler(async () => {
  const token = await verifySession()

  const data = await apiRequest({
    method: 'GET',
    endpoint: '/transactions/chart',
    token,
  })

  return data as TransChartPoint[]
})

export const fetchTransactionsPage = createServerFn().handler(async () => {
  const token = await verifySession()

  const data = await apiRequest({
    method: 'GET',
    endpoint: '/transactions/',
    token,
  })

  return data as ListResource<Transaction>
})

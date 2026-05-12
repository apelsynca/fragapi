import { createServerFn } from '@tanstack/react-start'
import type {
  Transaction,
  TransactionStats,
  TransChartPoint,
} from './models/transactions'
import type { ListResource } from './models/misc'
import { apiRequest } from './request'
import { verifySession } from '../lib/auth'

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

  const chartData = await apiRequest({
    method: 'GET',
    endpoint: '/transactions/chart',
    token,
  })

  return chartData as TransChartPoint[]
})

export const fetchTransactionsPage = createServerFn()
  .inputValidator((page: number) => page)
  .handler(async ({ data: page }) => {
    const token = await verifySession()

    const params = new URLSearchParams({
      page: page.toString(),
    })

    const listResource = await apiRequest({
      method: 'GET',
      endpoint: `/transactions/?${params.toString()}`,
      token,
    })

    return listResource as ListResource<Transaction>
  })

import { createServerFn } from '@tanstack/react-start'
import { verifySession } from '#/lib/auth'
import { apiRequest } from './request'
import type { ListResource } from './models/misc'
import type {
  FragmentTransaction,
  TransactionChartPoint,
  TransactionsStats,
} from './models/transactions'

export const fetchTransactionsPage = createServerFn()
  .validator((data: { page: number; sorting: string }) => data)
  .handler(async ({ data: { page, sorting } }) => {
    const token = await verifySession()
    console.log('fetching', page, sorting)

    return await apiRequest<ListResource<FragmentTransaction>>({
      method: 'GET',
      endpoint: `/transactions?page=${page}&sorting=${sorting}`,
      token,
    })
  })

export const fetchTransactionsStats = createServerFn().handler(async () => {
  const token = await verifySession()

  return await apiRequest<TransactionsStats>({
    method: 'GET',
    endpoint: '/transactions/stats',
    token,
  })
})

export const fetchTransactionsChart = createServerFn().handler(async () => {
  const token = await verifySession()

  return await apiRequest<TransactionChartPoint[]>({
    method: 'GET',
    endpoint: '/transactions/chart',
    token,
  })
})

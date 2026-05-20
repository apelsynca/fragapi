import { createServerFn } from '@tanstack/react-start'
import { verifySession } from '~/lib/auth'
import { apiRequest } from './request'
import type { ListResource } from './models/misc'
import type { FragmentTransaction } from '~/models/transactions'

export const fetchTransactionsPage = createServerFn()
  .inputValidator((data: { page: number; sorting: string }) => data)
  .handler(async ({ data: { page, sorting } }) => {
    const token = await verifySession()
    console.log('fetching', page, sorting)

    const resp = await apiRequest<ListResource<FragmentTransaction>>({
      method: 'GET',
      endpoint: `/transactions?page=${page}&sorting=${sorting}`,
      token,
    })

    console.log(resp)

    return resp
  })

interface TransactionsStats {
  totalSpend: number
  starsTotalSpend: number
  premiumTotalSpend: number
}

export const fetchTransactionsStats = createServerFn().handler(async () => {
  const token = await verifySession()

  return await apiRequest<TransactionsStats>({
    method: 'GET',
    endpoint: '/transactions/stats',
    token,
  })
})

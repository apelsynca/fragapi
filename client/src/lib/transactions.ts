import { createServerFn } from '@tanstack/react-start'
import type { TransactionStats } from './models/transactions'
import { apiRequest } from './request'

export const fetchTransactionStats = createServerFn().handler(async () => {
  return (await apiRequest({
    data: {
      method: 'GET',
      endpoint: '/panel/transactions/stats',
    },
  })) as TransactionStats
})

import { queryOptions } from '@tanstack/react-query'
import { fetchMe } from '#/server-api/user'
import { fetchTonRate } from '#/server-api/ton'
import {
  fetchTransactionsChart,
  fetchTransactionsPage,
  fetchTransactionsStats,
} from '#/server-api/transactions'
import { fetchApiTokens } from '#/server-api/api-tokens'
import { fetchTonPaymentHistory } from '#/server-api/deposits'

export const userMeOptions = () =>
  queryOptions({
    queryKey: ['users', 'me'],
    queryFn: () => fetchMe(),
  })

export const tonRateOptions = () =>
  queryOptions({
    queryKey: ['rate'],
    queryFn: () => fetchTonRate(),
  })

export const transactionsListOptions = (page: number) =>
  queryOptions({
    queryKey: ['transactions', 'list', page],
    queryFn: () =>
      fetchTransactionsPage({ data: { page, sorting: '-created_at' } }),
  })

export const transactionsStatsOptions = () =>
  queryOptions({
    queryKey: ['transactions', 'stats'],
    queryFn: () => fetchTransactionsStats(),
  })

export const transactionChartOptions = () =>
  queryOptions({
    queryKey: ['transactions', 'chart'],
    queryFn: () => fetchTransactionsChart(),
  })

export const apiTokensOptions = () =>
  queryOptions({
    queryKey: ['api-tokens'],
    queryFn: () => fetchApiTokens(),
  })

export const paymentHistoryOptions = (page: number) =>
  queryOptions({
    queryKey: ['payments', 'history', page],
    queryFn: () => fetchTonPaymentHistory({ data: page }),
  })

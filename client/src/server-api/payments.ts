import { createServerFn } from '@tanstack/react-start'
import { apiRequest } from './request'
import { verifySession } from '../lib/auth'
import type { TonConnectMessage } from '#/server-api/models/message'
import type { ListResource } from './models/misc'
import type { Payment } from './models/payments'

export const requestTonPayment = createServerFn({ method: 'POST' })
  .validator((amount: number) => amount)
  .handler(async ({ data }) => {
    const token = await verifySession()

    return await apiRequest<TonConnectMessage>({
      method: 'POST',
      endpoint: `/payments/ton?amount=${data}`,
      token,
    })
  })

export const fetchTonPaymentHistory = createServerFn({ method: 'GET' })
  .validator((page: number) => page)
  .handler(async ({ data: page }) => {
    const token = await verifySession()

    return await apiRequest<ListResource<Payment>>({
      method: 'GET',
      endpoint: `/payments/?page=${page}`,
      token,
    })
  })

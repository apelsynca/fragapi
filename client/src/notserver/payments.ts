import { createServerFn } from '@tanstack/react-start'
import type { TonConnectMessage } from '~/notserver/models/message'
import { apiRequest } from './request'
import { verifySession } from '../lib/auth'

export const requestTonPayment = createServerFn({ method: 'POST' })
  .inputValidator((amount: number) => amount)
  .handler(async ({ data }) => {
    const token = await verifySession()

    return await apiRequest<TonConnectMessage>({
      method: 'POST',
      endpoint: `/payments/ton?amount=${data}`,
      token,
    })
  })

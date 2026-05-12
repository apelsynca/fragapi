import { createServerFn } from '@tanstack/react-start'
import type { TonConnectMessage } from './models/message'
import { apiRequest } from './request'
import { verifySession } from '../lib/auth'

export const requestTonPayment = createServerFn({ method: 'POST' })
  .inputValidator((amount: number) => amount)
  .handler(async ({ data }) => {
    const token = await verifySession()

    return await apiRequest<TonConnectMessage>({
      method: 'GET',
      endpoint: `/payments/ton?amount=${data}`,
      token,
    })
  })

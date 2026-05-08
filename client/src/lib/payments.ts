import { createServerFn } from '@tanstack/react-start'
import { apiRequest } from './request'
import type { TonConnectMessage } from './models/message'

export const requestTonPayment = createServerFn({ method: 'POST' })
  .inputValidator((amount: number) => amount)
  .handler(async ({ data }) => {
    return (await apiRequest({
      data: {
        method: 'GET',
        endpoint: `/payments/ton?amount=${data}`,
      },
    })) as TonConnectMessage
  })

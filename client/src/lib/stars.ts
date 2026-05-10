import { createServerFn } from '@tanstack/react-start'
import { verifySession } from './auth'
import { apiRequest } from './request'
import type { BaseRecipient } from './models/recipient'

export const searchStarsRecipientFn = createServerFn({ method: 'GET' })
  .inputValidator((data: { username: string; quantity?: number }) => data)
  .handler(async ({ data }) => {
    const token = await verifySession()

    const abc: any = {}
    if (data.quantity !== undefined) {
      abc['quantity'] = data.quantity.toString()
    }

    const urlParams = new URLSearchParams(abc)

    const recipientData = await apiRequest({
      method: 'GET',
      endpoint: `/stars/recipient/${data.username}?${urlParams}`,
      token,
    })

    return recipientData as BaseRecipient
  })

import { createServerFn } from '@tanstack/react-start'
import { verifySession } from './auth'
import { apiRequest } from './request'
import type { BaseRecipient } from './models/recipient'

export const searchStarsRecipientFn = createServerFn({ method: 'GET' })
  .inputValidator((data: { username: string; quantity?: number }) => data)
  .handler(async ({ data }) => {
    const token = await verifySession()

    const params: { quantity?: string } = {}
    if (data.quantity !== undefined) {
      params.quantity = data.quantity.toString()
    }

    const urlParams = new URLSearchParams(params)

    const recipientData = await apiRequest({
      method: 'GET',
      endpoint: `/stars/recipient/${data.username}?${urlParams}`,
      token,
    })

    return recipientData as BaseRecipient
  })

interface BuyData {
  username: string
  quantity: number
}

export const buyStarsFn = createServerFn({})
  .inputValidator((data: BuyData) => data)
  .handler(async ({ data }) => {
    const token = await verifySession()

    const buyResp = await apiRequest({
      method: 'POST',
      endpoint: '/stars/buy',
      payload: data,
      token,
    })
    return buyResp as { messageHash: string }
  })

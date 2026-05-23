import { createServerFn } from '@tanstack/react-start'
import type { User, RevokeTokenResponse } from './models/users'
import { apiRequest } from './request'
import { verifySession } from '../lib/auth'

export const fetchMe = createServerFn().handler(async () => {
  const token = await verifySession()

  return await apiRequest<User>({
    method: 'GET',
    endpoint: '/panel/users/me',
    token,
  })
})

export const revokeApiToken = createServerFn({ method: 'POST' }).handler(
  async () => {
    const token = await verifySession()

    return await apiRequest<RevokeTokenResponse>({
      method: 'POST',
      endpoint: '/panel/users/revoke_api_token',
      token,
    })
  },
)

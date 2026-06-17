import { createServerFn } from '@tanstack/react-start'
import { verifySession } from '#/lib/auth'
import { apiRequest } from './request'
import type { ApiToken } from '#/server-api/models/api-token'

export const fetchApiTokens = createServerFn({ method: 'GET' }).handler(
  async () => {
    const token = await verifySession()

    return await apiRequest<ApiToken[]>({
      method: 'GET',
      endpoint: '/api-tokens',
      token,
    })
  },
)

export const createApiTokenFn = createServerFn({ method: 'POST' })
  .validator((data: { name: string }) => data)
  .handler(async ({ data: { name } }) => {
    const token = await verifySession()

    return await apiRequest<ApiToken>({
      method: 'POST',
      endpoint: '/api-tokens',
      token,
      payload: { name },
    })
  })

export const deleteApiTokenFn = createServerFn({ method: 'POST' })
  .validator((id: string) => id)
  .handler(async ({ data: id }) => {
    const token = await verifySession()

    return await apiRequest<null>({
      method: 'DELETE',
      endpoint: `/api-tokens/${id}`,
      token,
    })
  })

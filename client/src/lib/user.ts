import { createServerFn } from '@tanstack/react-start'
import type { User } from './models/users'
import { apiRequest } from './request'
import { verifySession } from './auth'

export const fetchMe = createServerFn().handler(async () => {
  const token = await verifySession()

  return await apiRequest<User>({
    method: 'GET',
    endpoint: '/panel/users/me',
    token,
  })
})

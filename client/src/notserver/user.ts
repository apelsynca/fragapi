import { createServerFn } from '@tanstack/react-start'
import type { User } from './models/users'
import { apiRequest } from './request'
import { verifySession } from '../lib/auth'

export const fetchMe = createServerFn().handler(async () => {
  const token = await verifySession()

  return await apiRequest<User>({
    method: 'GET',
    endpoint: '/users/me',
    token,
  })
})

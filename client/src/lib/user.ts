import { createServerFn } from '@tanstack/react-start'
import type { User } from './models/users'
import { apiRequest } from './request'
import { verifySession } from './auth'

export const fetchMe = createServerFn().handler(async () => {
  const token = await verifySession()

  const data = await apiRequest({
    method: 'GET',
    endpoint: '/panel/users/me',
    token,
  })

  return data as User
})

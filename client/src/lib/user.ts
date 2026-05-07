import { createServerFn } from '@tanstack/react-start'
import { verifySession } from './auth'
import { doRequest } from './request'
import type { User } from './models/users'

export const fetchMe = createServerFn().handler(async () => {
  const token = await verifySession()

  const response = await doRequest({
    method: 'GET',
    endpoint: '/panel/users/me',
    token,
  })

  return (await response.json()) as User
})

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

  const json = await response.json()

  console.log(json)

  return json as User
})

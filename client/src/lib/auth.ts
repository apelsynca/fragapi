import { redirect } from '@tanstack/react-router'
import { createServerFn } from '@tanstack/react-start'

import { useAppSession } from './session'

export const fetchSessionToken = createServerFn({ method: 'GET' }).handler(
  async () => {
    const session = await useAppSession()

    if (!session.data.token) {
      return null
    }

    return session.data.token
  },
)

export const verifySession = createServerFn({ method: 'GET' }).handler(
  async () => {
    const token = await fetchSessionToken()

    if (!token) {
      throw redirect({ href: '/' })
    }

    return token
  },
)

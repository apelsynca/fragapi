import { redirect } from '@tanstack/react-router'
import { createServerFn } from '@tanstack/react-start'

import { useAppSession } from './session'
import { doRequest } from './request'

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

export const botHashLoginFn = createServerFn({ method: 'POST' })
  .inputValidator((hash: string) => hash)
  .handler(async ({ data: hash }) => {
    const response = await doRequest({
      method: 'POST',
      endpoint: '/auth/tgbot',
      json: {
        hash,
      },
    })

    if (!response.ok) {
      throw redirect({ to: '/' })
    }

    const { token, success } = (await response.json()) as {
      token: string
      success: boolean
    }

    if (success !== true) {
      throw redirect({ to: '/' })
    }

    const session = await useAppSession()
    await session.update({ token })
  })

export const logoutFn = createServerFn({ method: 'POST' }).handler(async () => {
  const session = await useAppSession()
  session.clear()

  throw redirect({
    href: '/',
  })
})

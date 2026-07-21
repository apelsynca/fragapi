import { redirect } from '@tanstack/react-router'
import { createServerFn } from '@tanstack/react-start'

import { useAppSession } from '../lib/session'

export const botHashLoginFn = createServerFn({ method: 'POST' })
  .validator((hash: string) => hash)
  .handler(async ({ data: hash }) => {
    const defaultHeaders = { 'Content-Type': 'application/json' }

    const response = await fetch(`${process.env.BACKEND_ENDPOINT}/auth/tgbot`, {
      method: 'POST',
      headers: defaultHeaders,
      body: JSON.stringify({ hash }),
    })

    if (!response.ok) {
      console.warn('Bot hash login request status is not OK')
      throw redirect({ to: '/' }) // NOTE: can redirect to /bad-login or smth, or just return info about bad login
    }

    const { token, success } = (await response.json()) as {
      token: string
      success: boolean
    }

    if (success !== true) {
      console.warn('Unsuccessful bot hash login request')
      throw redirect({ to: '/' }) // Same for this part
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

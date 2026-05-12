import { redirect } from '@tanstack/react-router'
import { createServerFn } from '@tanstack/react-start'

import { useAppSession } from '../lib/session'

export const botHashLoginFn = createServerFn({ method: 'POST' })
  .inputValidator((hash: string) => hash)
  .handler(async ({ data: hash }) => {
    const defaultHeaders = { 'Content-Type': 'application/json' }

    const response = await fetch(`${process.env.BACKEND_ENDPOINT}/auth/tgbot`, {
      method: 'POST',
      headers: defaultHeaders,
      body: JSON.stringify({ hash }),
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

import { redirect } from '@tanstack/react-router'
import { createServerFn } from '@tanstack/react-start'

import { useAppSession } from './session'

export const fetchUser = createServerFn({ method: 'GET' }).handler(async () => {
  const session = await useAppSession()

  if (!session.data.token) {
    return null
  }

  return {
    token: session.data.token,
  }
})

export const botHashLoginFn = createServerFn({ method: 'POST' })
  .inputValidator((hash: string) => hash)
  .handler(async ({ data: hash }) => {
    const response = await fetch('http://localhost:8000/v1/auth/tgbot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
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

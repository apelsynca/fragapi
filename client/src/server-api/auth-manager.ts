import { redirect } from '@tanstack/react-router'
import { createServerFn } from '@tanstack/react-start'

import { useAppSession } from '../lib/session'

export type BotLoginResult =
  | { ok: true }
  | { ok: false; reason: 'invalid' | 'server_error' }

export const botHashLoginFn = createServerFn({ method: 'POST' })
  .validator((hash: string) => hash)
  .handler(async ({ data: hash }): Promise<BotLoginResult> => {
    const defaultHeaders = { 'Content-Type': 'application/json' }

    const response = await fetch(`${process.env.BACKEND_ENDPOINT}/auth/tgbot`, {
      method: 'POST',
      headers: defaultHeaders,
      body: JSON.stringify({ hash }),
    })

    if (!response.ok) {
      return {
        ok: false,
        reason: response.status === 404 ? 'invalid' : 'server_error',
      }
    }

    const json = (await response.json().catch(() => null)) as {
      token: string
      success: boolean
    } | null

    if (json?.success !== true) {
      return { ok: false, reason: 'invalid' }
    }

    const session = await useAppSession()
    await session.update({ token: json.token })

    return { ok: true }
  })

export const logoutFn = createServerFn({ method: 'POST' }).handler(async () => {
  const session = await useAppSession()
  await session.clear()

  throw redirect({
    to: '/',
  })
})

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

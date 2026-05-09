import { useSession } from '@tanstack/react-start/server'
import { SESSION_PASSWORD } from '#/env'

type SessionUser = {
  token: string
}

export function useAppSession() {
  return useSession<SessionUser>({
    password: SESSION_PASSWORD!,
  })
}

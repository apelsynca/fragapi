import { useSession } from '@tanstack/react-start/server'

type SessionUser = {
  token: string
}

export function useAppSession() {
  return useSession<SessionUser>({
    password: process.env.SESSION_PASSWORD!,
  })
}

import { useSession } from '@tanstack/react-start/server'

type SessionUser = {
  token: string
}

const SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 7 // 7 days, matches server USER_SESSION_TTL

export function useAppSession() {
  return useSession<SessionUser>({
    password: process.env.SESSION_PASSWORD!,
    maxAge: SESSION_MAX_AGE_SECONDS,
    cookie: { sameSite: 'lax' },
  })
}

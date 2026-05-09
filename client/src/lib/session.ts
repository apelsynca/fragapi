import { useSession } from '@tanstack/react-start/server'

type SessionUser = {
  token: string
}

export function useAppSession() {
  return useSession<SessionUser>({
    password: 'AAAKdkxXXXX1231231kaKKKKKKKKKKasdaskdaskKKKKKK',
  })
}

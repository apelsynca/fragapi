import { createFileRoute, redirect } from '@tanstack/react-router'
import { botHashLoginFn } from '#/server-api/auth-manager'

type LoginSearch = {
  hash: string
}

export const Route = createFileRoute('/bot-login')({
  validateSearch: (search: Record<string, unknown>): LoginSearch => {
    return {
      hash: (search.hash as string) || '',
    }
  },
  loaderDeps: ({ search }) => {
    return { hash: search.hash }
  },
  loader: async ({ deps }) => {
    if (!deps.hash) {
      throw new Error('Missing hash')
    }

    await botHashLoginFn({ data: deps.hash })

    throw redirect({ to: '/dashboard' })
  },
  errorComponent: ({ error }) => {
    if (error.message === 'Missing hash') {
      return <p>No hash broo</p>
    }

    throw error
  },
})

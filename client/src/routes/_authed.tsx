import Landing from '~/components/Landing'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_authed')({
  beforeLoad: ({ context }) => {
    if (!context.token) {
      throw new Error('Not authenticated')
    }
  },
  errorComponent: ({ error }) => {
    if (error.message === 'Not authenticated') {
      return <Landing />
    }

    throw error
  },
})

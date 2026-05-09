import { createFileRoute, redirect } from '@tanstack/react-router'
import Landing from '~/components/Landing'

export const Route = createFileRoute('/')({
  component: App,
  beforeLoad: ({ context }) => {
    if (context.token !== null) {
      throw redirect({ to: '/dashboard' })
    }
  },
})

// if already logged in -> redirect

function App() {
  const context = Route.useRouteContext()

  return <Landing toPanel={context.token ? true : false} />
}

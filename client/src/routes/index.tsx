import { createFileRoute } from '@tanstack/react-router'
import Landing from '~/components/Landing'
import { ThemeProvider } from '~/components/theme-provider'

export const Route = createFileRoute('/')({
  // NOTE: here we are forcing dark theme for the landing page.
  component: () => <IndexRoute />,
})

function IndexRoute() {
  const context = Route.useRouteContext()

  return (
    <ThemeProvider defaultTheme="dark" storageKey="landing-theme">
      <Landing toPanel={context.token ? true : false} />
    </ThemeProvider>
  )
}

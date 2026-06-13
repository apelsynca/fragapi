import { createFileRoute } from '@tanstack/react-router'
import Landing from '~/components/Landing'
import { ThemeProvider } from '~/components/theme-provider'

export const Route = createFileRoute('/')({
  // NOTE: here we are forcing dark theme for the landing page.
  component: () => (
    <ThemeProvider defaultTheme="dark" storageKey="landing-theme">
      <Landing />
    </ThemeProvider>
  ),
})

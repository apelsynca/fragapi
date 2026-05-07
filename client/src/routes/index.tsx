import { ExternalLink } from 'lucide-react'
import { createFileRoute, Link, redirect } from '@tanstack/react-router'
import { Button } from '#/components/ui/button'

export const Route = createFileRoute('/')({
  component: App,
  beforeLoad: ({ context }) => {
    if (context.user !== null) {
      throw redirect({ to: '/dashboard' })
    }
  },
})

// if already logged in -> redirect

function App() {
  const context = Route.useRouteContext()

  return (
    <main className="flex min-h-screen items-center justify-center">
      <div className="flex flex-col gap-6 max-w-xl pb-20">
        <div className="flex flex-col gap-2">
          <h1 className="text-4xl font-bold text-center">FragAPI</h1>
          <p className="text-lg text-center text-gray-100">
            Весь функционал fragment, без KYC, без 24-х слов, в виде API.
          </p>
        </div>

        <div className="flex justify-center gap-1">
          {context.user ? (
            <Button asChild>
              <Link to="/dashboard">В панель</Link>
            </Button>
          ) : (
            <Button asChild>
              <a href="https://t.me/fragauthbot?start=login">
                Войти через бота
              </a>
            </Button>
          )}
          <Button asChild variant="secondary">
            <a href="https://docs.fragapi.com">
              Узнать больше <ExternalLink />
            </a>
          </Button>
        </div>
      </div>
    </main>
  )
}

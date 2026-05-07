import { ExternalLink } from 'lucide-react'
import { createFileRoute } from '@tanstack/react-router'
import { Button } from '#/components/ui/button'

export const Route = createFileRoute('/')({ component: App })

// if already logged in -> redirect

function App() {
  return (
    <main>
      <div className="flex flex-col gap-4 max-w-128 m-auto">
        <div>
          <h1 className="font-semibold text-center">Fragment API</h1>
          <p className="text-center">abc</p>
        </div>

        <div className="flex justify-center gap-1">
          <Button asChild>
            <a href="https://t.me/fragauthbot">Войти через бота</a>
          </Button>
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

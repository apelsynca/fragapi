import { Link } from '@tanstack/react-router'
import { Button } from './ui/button'
import { ExternalLink } from 'lucide-react'

export default function Landing({ toPanel = false }: { toPanel?: boolean }) {
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
          {toPanel ? (
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

import { Button } from '#/components/ui/button'
import { Link } from '@tanstack/react-router'
import { HomeIcon } from 'lucide-react'

export default function NotFoundPage() {
  return (
    <main className="grid min-h-screen place-items-center bg-[#090b0c] px-6 py-24 sm:py-32 lg:px-8">
      <div className="text-center">
        <p className="text-base font-semibold text-[#fdba72]">404</p>
        <h1 className="mt-4 text-5xl font-semibold tracking-tight text-balance text-white sm:text-7xl">
          Page not found
        </h1>
        <p className="mt-6 text-lg font-medium text-pretty text-gray-400 sm:text-xl/8">
          Sorry, we couldn’t find the page you’re looking for.
        </p>
        <div className="mt-10 flex items-center justify-center gap-x-6">
          <Button size="lg" asChild>
            <Link to="/" className="dark">
              <HomeIcon /> Go back home
            </Link>
          </Button>
        </div>
      </div>
    </main>
  )
}

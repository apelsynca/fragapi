import { createFileRoute, redirect } from '@tanstack/react-router'
import { botHashLoginFn } from '#/server-api/auth-manager'
import { m } from '#/paraglide/messages'
import { siteConfig } from '#/config'

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
      return { status: 'missing_hash' as const }
    }

    const result = await botHashLoginFn({ data: deps.hash })

    if (result.ok) {
      throw redirect({ to: '/dashboard' })
    }

    return { status: 'failed' as const, reason: result.reason }
  },
  component: BotLoginComponent,
})

function BotLoginComponent() {
  const data = Route.useLoaderData()

  if (data.status === 'missing_hash') {
    return <div className="p-4">{m.bot_login_missing_hash()}</div>
  }

  // status === 'failed' (success redirects from the loader)
  const botLink = `https://t.me/${siteConfig.botUsername}`
  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <div className="text-center space-y-4 max-w-sm">
        <h2 className="text-lg font-semibold">
          {data.reason === 'invalid'
            ? m.bot_login_invalid_link()
            : m.bot_login_server_error()}
        </h2>
        <p className="text-muted-foreground text-sm">
          {m.bot_login_try_again()}
        </p>
        <a
          href={botLink}
          className="inline-block px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90"
        >
          {m.bot_login_get_new_link()}
        </a>
      </div>
    </div>
  )
}

/// <reference types="vite/client" />
import type { QueryClient } from '@tanstack/react-query'
import {
  ErrorComponent,
  HeadContent,
  Outlet,
  Scripts,
  createRootRouteWithContext,
} from '@tanstack/react-router'
import { fetchSessionToken } from '~/lib/auth'
import { TanStackDevtools } from '@tanstack/react-devtools'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'

import globalsCss from '~/styles/globals.css?url'
import utilsCss from '~/styles/utils.css?url'
import { seo } from '~/utils/seo'
import { getLocale } from '~/paraglide/runtime'
import { m } from '~/paraglide/messages'

export const Route = createRootRouteWithContext<{
  queryClient: QueryClient
}>()({
  beforeLoad: async () => {
    const token = await fetchSessionToken()
    return { token }
  },
  head: () => ({
    meta: [
      {
        charSet: 'utf-8',
      },
      {
        name: 'viewport',
        content: 'width=device-width, initial-scale=1',
      },
      ...seo({
        title: 'FragAPI',
        description: m.seo_description(),
        keywords: 'fragapi,fragment,frag',
      }),
    ],
    links: [
      {
        rel: 'stylesheet',
        href: globalsCss,
      },
      {
        rel: 'stylesheet',
        href: utilsCss,
      },
    ],
  }),
  component: RootComponent,
  errorComponent: ({ error }) => {
    return (
      <div className="p-4 bg-red-100 text-red-900 dark:bg-red-900 dark:text-red-100 rounded">
        <ErrorComponent error={error} />
      </div>
    )
  },
  notFoundComponent: () => {
    return <div>Basic not found</div>
  },
})

function RootComponent() {
  return (
    <RootDocument>
      <Outlet />
    </RootDocument>
  )
}

function RootDocument({ children }: { children: React.ReactNode }) {
  const locale = getLocale()

  return (
    <html lang={locale} suppressHydrationWarning>
      <head>
        <HeadContent />
      </head>
      <body>
        {children}
        <TanStackDevtools
          config={{
            position: 'bottom-right',
          }}
          plugins={[
            {
              name: 'Tanstack Router',
              render: <TanStackRouterDevtools />,
            },
          ]}
        />
        <Scripts />
      </body>
    </html>
  )
}

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
import { I18nextProvider } from 'react-i18next'

import i18n from '~/lib/i18n-config'
import { getLocale } from '~/lib/i18n'
import globalsCss from '../styles/globals.css?url'
import utilsCss from '../styles/utils.css?url'
import { seo } from '~/utils/seo'

const THEME_INIT_SCRIPT = `(function(){try{var stored=window.localStorage.getItem('theme');var mode=(stored==='light'||stored==='dark'||stored==='auto')?stored:'auto';var prefersDark=window.matchMedia('(prefers-color-scheme: dark)').matches;var resolved=mode==='auto'?(prefersDark?'dark':'light'):mode;var root=document.documentElement;root.classList.remove('light','dark');root.classList.add(resolved);if(mode==='auto'){root.removeAttribute('data-theme')}else{root.setAttribute('data-theme',mode)}root.style.colorScheme=resolved;}catch(e){}})();`

export const Route = createRootRouteWithContext<{
  queryClient: QueryClient
}>()({
  beforeLoad: async () => {
    getLocale()
    const token = await fetchSessionToken()

    return {
      token,
    }
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
        description_en: 'API for interaction with Fragment, no KYC',
        keywords: 'fragment,frag,fragapi',
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
})

function RootComponent() {
  return (
    <RootDocument>
      <Outlet />
    </RootDocument>
  )
}

function RootDocument({ children }: { children: React.ReactNode }) {
  const lang = i18n.language

  return (
    <html lang={lang} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
        <HeadContent />
      </head>
      <body>
        <I18nextProvider i18n={i18n}>{children}</I18nextProvider>
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

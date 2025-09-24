/// <reference types="vite/client" />
import type { ReactNode } from "react";
import {
  Outlet,
  HeadContent,
  Scripts,
  createRootRouteWithContext,
} from "@tanstack/react-router";
import type { QueryClient } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";

import globalsCss from "./globals.css?url";
import appCss from "./app.css?url";
import { DefaultNotFound } from "~/components/not-found";

export const Route = createRootRouteWithContext<{
  queryClient: QueryClient;
}>()({
  head: () => ({
    links: [
      {
        rel: "stylesheet",
        href: globalsCss,
      },
      {
        rel: "stylesheet",
        href: appCss,
      },
    ],
    meta: [
      {
        charSet: "utf-8",
      },
      {
        name: "viewport",
        content: "width=device-width, initial-scale=1",
      },
      {
        title: "Fragment API",
      },
      {
        name: "description",
        content: "Удобное API фрагмента",
      },
      { name: "og:type", content: "website" },
      { name: "og:title", content: "Fragment API" },
      {
        name: "og:description",
        content: "Лучшее апи фрагмента, без KYC, без суеты",
      },
    ],
  }),
  component: RootComponent,
  notFoundComponent: DefaultNotFound,
});

function RootComponent() {
  return (
    <RootDocument>
      <Outlet />
    </RootDocument>
  );
}

function RootDocument({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="ru">
      <head>
        <HeadContent />
      </head>
      <body className="dark">
        {children}
        <Scripts />
        <ReactQueryDevtools initialIsOpen={false} />
      </body>
    </html>
  );
}

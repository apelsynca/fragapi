import {
  createRootRoute,
  HeadContent,
  Outlet,
  Scripts,
  useParams,
} from "@tanstack/react-router";
import appCss from "@/styles/app.css?url";
import { RootProvider } from "fumadocs-ui/provider/tanstack";
import { i18nProvider } from "fumadocs-ui/i18n";
import { translations } from "@/lib/layout.shared";

export const Route = createRootRoute({
  head: () => ({
    meta: [
      {
        charSet: "utf-8",
      },
      {
        name: "viewport",
        content: "width=device-width, initial-scale=1",
      },
      {
        title: "FragAPI Documentation",
      },
    ],
    links: [{ rel: "stylesheet", href: appCss }],
  }),
  component: RootComponent,
});

function RootComponent() {
  const { lang } = useParams({ strict: false });

  return (
    <html suppressHydrationWarning>
      <head>
        <HeadContent />
      </head>
      <body className="flex flex-col min-h-screen">
        <RootProvider
          i18n={i18nProvider(translations, lang)}
          search={{ enabled: false }}
        >
          <Outlet />
        </RootProvider>
        <Scripts />
      </body>
    </html>
  );
}

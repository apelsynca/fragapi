import { createFileRoute } from "@tanstack/react-router";

import { getSession } from "~/lib/auth";
import { AppHero } from "~/components/hero";

export const Route = createFileRoute("/")({
  component: RouteComponent,
  loader: async () => {
    const { token } = await getSession();

    if (token) {
      return true;
    } else {
      return false;
    }
  },
});

function RouteComponent() {
  const isLoggedIn = Route.useLoaderData();

  return <AppHero isLoggedIn={isLoggedIn} />;
}

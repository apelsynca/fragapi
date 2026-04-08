import { createRouter as createTanStackRouter } from "@tanstack/react-router";
import { setupRouterSsrQueryIntegration } from "@tanstack/react-router-ssr-query";
import { queryClient } from "~/lib/query";

import { routeTree } from "./routeTree.gen";

export function getRouter() {
  const router = createTanStackRouter({
    routeTree,
    context: { queryClient },
    scrollRestoration: true,
    scrollRestorationBehavior: "smooth",
    defaultPreload: "intent",
  });

  setupRouterSsrQueryIntegration({
    router,
    queryClient,
  });

  return router;
}

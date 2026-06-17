import { openapi } from "@/lib/openapi";
import { createFileRoute } from "@tanstack/react-router";

const proxy = openapi.createProxy({
  // optional, we recommend to set a list of allowed origins for proxied requests
  allowedOrigins: ["https://api.fragapi.com"],
});

export const Route = createFileRoute("/api/proxy")({
  server: {
    handlers: {
      // Handles all methods by default, or specify individual methods (GET, POST, etc.)
      ANY: async ({ request }) => {
        return proxy.handle(request);
      },
    },
  },
});

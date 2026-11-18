import { createOpenAPI } from "fumadocs-openapi/server";

export const openapiUrl =
  process.env.OPENAPI_URL || "https://api.fragapi.com/openapi.json";

// note: this is a server-side API
export const openapi = createOpenAPI({
  // the OpenAPI schema, you can also give it an external URL.
  input: [openapiUrl],
  proxyUrl: "/api/proxy",
});

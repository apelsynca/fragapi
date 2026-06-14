import { createOpenAPI } from "fumadocs-openapi/server";

// note: this is a server-side API
export const openapi = createOpenAPI({
  // the OpenAPI schema, you can also give it an external URL.
  input: ["https://api.fragapi.com/openapi.json"],
});

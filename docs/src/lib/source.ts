import { loader } from "fumadocs-core/source";
import { docs } from "collections/server";
import { lucideIconsPlugin } from "fumadocs-core/source/lucide-icons";
import { docsRoute } from "./shared";
import { openapiPlugin } from "fumadocs-openapi/server";
import { i18n } from "./i18n";
import { cleanMarkdown } from "./clean-markdown";
import { loadOperations, renderOperation } from "./openapi-markdown";
import { siteUrl } from "./site";

export const source = loader({
  source: docs.toFumadocsSource(),
  baseUrl: docsRoute,
  plugins: [lucideIconsPlugin(), openapiPlugin()],
  i18n,
});

export function markdownPathToSlugs(segs: string[]) {
  if (segs.length === 0) return [];

  const out = [...segs];
  out[out.length - 1] = out[out.length - 1].replace(/\.md$/, "");
  if (out.length === 1 && out[0] === "index") out.pop();
  return out;
}

export function slugsToMarkdownPath(slugs: string[]) {
  const segments = [...slugs];
  if (segments.length === 0) {
    segments.push("index.md");
  } else {
    segments[segments.length - 1] += ".md";
  }

  return {
    segments,
    url: `${docsRoute}/${segments.join("/")}`,
  };
}

type DocsPage = (typeof source)["$inferPage"];

/** Generated API pages live at `api/<tag>/<name>`, named after `<tag>:<name>`. */
export function pageOperationId(page: DocsPage) {
  return page.slugs[0] === "api" ? page.slugs.slice(1).join(":") : undefined;
}

export function pageMarkdownUrl(page: DocsPage) {
  const path = page.slugs.length > 0 ? page.slugs.join("/") : "index";
  return `${siteUrl}/${page.locale ?? i18n.defaultLanguage}/docs/${path}.md`;
}

async function getPageBody(page: DocsPage) {
  const operationId = pageOperationId(page);
  if (operationId) {
    const { doc, operations } = await loadOperations();
    const operation = operations.get(operationId);
    if (operation) return renderOperation(doc, operation);
  }
  return cleanMarkdown(await page.data.getText("processed"));
}

export async function getLLMText(page: DocsPage) {
  return `# ${page.data.title} (${siteUrl}${page.url})

${await getPageBody(page)}`;
}

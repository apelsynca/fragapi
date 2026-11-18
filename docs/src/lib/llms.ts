import type { Node } from "fumadocs-core/page-tree";
import { i18n } from "./i18n";
import { loadOperations, operationSummary } from "./openapi-markdown";
import type { OperationRef } from "./openapi-markdown";
import { apiUrl, dashboardUrl, sandboxApiUrl, siteUrl } from "./site";
import { getLLMText, pageMarkdownUrl, pageOperationId, source } from "./source";

/** English first: it is what most models and tools will read. */
export const llmsLanguages = ["en", "ru"] as const;

const sectionTitle: Record<string, string> = {
  en: "Docs (English)",
  ru: "Документация (Русский) — guides only, the API reference is in English",
};

export const markdownHeaders = {
  "Content-Type": "text/markdown; charset=utf-8",
};

export function notFoundResponse() {
  return new Response("Not found\n", { status: 404 });
}

export function isDocsLanguage(lang: string) {
  return (i18n.languages as readonly string[]).includes(lang);
}

const intro = `# FragAPI

> FragAPI is an open-source HTTP API for automating fragment.com: buy Telegram Stars and Telegram Premium for any username, look up Telegram gift models, and top up a balance in TON. No KYC and no wallet seed phrase are needed; purchases are paid from a prepaid balance.

## Basics

- Base URL: \`${apiUrl}/v1\`. Sandbox environment: \`${sandboxApiUrl}/v1\`; its responses carry the \`X-Frag-Sandbox: 1\` header.
- Auth: send \`Authorization: Bearer <API token>\` on every request. Tokens are created at ${dashboardUrl}/dashboard/api-tokens (a name and an expiry date). A token works for every endpoint below, except the few marked "dashboard session only".
- Requests and responses are JSON with camelCase fields (\`showSender\`, \`transactionId\`).
- Usernames are accepted as \`synca\`, \`@synca\` or \`https://t.me/synca\`.
- Amounts, prices and the balance are in GRAM.
- Purchases are charged to the account balance, with a commission of about 2% (1.8% plus the network fee). A purchase fails with \`InsufficientFunds\` when the balance is too low.

## Typical flow

1. \`GET /v1/users/me\`: check the balance.
2. If it is too low, \`POST /v1/deposits/ton?amount=<GRAM>\` (or \`/v1/deposits/ton/memo\`) and send a TON transfer to the returned address with the returned payload (or memo). The balance is credited once the transfer is seen.
3. Optional: \`GET /v1/stars/recipient/{username}\` or \`GET /v1/premium/recipient/{username}\` to check that the user exists and can receive the purchase.
4. \`POST /v1/stars/buy\` with \`{"username": "synca", "quantity": 50}\`, or \`POST /v1/premium/buy\` with \`{"username": "synca", "months": 3}\`. This is a real purchase: the response has the amount charged and the transaction id.
5. \`GET /v1/transactions\`: history of purchases, paginated with \`page\` and \`limit\`.

## Limits

- Stars: 50 to 10,000,000 per purchase.
- Premium: 3, 6 or 12 months.
- Bulk Stars: 1 to 100 recipients in \`POST /v1/stars/buy/bulk\`. It responds \`202\` right away; poll \`GET /v1/stars/buy/bulk/{id}\` until \`status\` is \`done\`, then read each item's \`result\` or \`error\`. Only the items that were bought are charged.
- Rate limits: 500 requests per minute per account, and 90 per minute on the buy endpoints. Going over the buy limit blocks buying for 5 minutes.
- Lists are paginated: \`page\` starts at 1, \`limit\` is 10 by default and 100 at most.

## Errors

Errors are \`{"error": "<name>", "detail": "<what went wrong>"}\`:

- \`400 BadRequest\`: the request can't be done; \`detail\` says why.
- \`400 InsufficientFunds\`: the balance is too low; \`detail\` has the amount needed.
- \`401 Unauthorized\`: the token is missing, invalid or expired.
- \`404 ResourceNotFound\`: for example, a username that does not exist.
- \`422 RequestValidationError\`: the request is malformed; \`detail\` is a list of field errors.
- \`429\`: rate limited, with no JSON body. Retry later.

## Example

\`\`\`bash
curl -X POST "${apiUrl}/v1/stars/buy" \\
  -H "Authorization: Bearer $FRAGAPI_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"username": "synca", "quantity": 50}'
\`\`\`

## Python SDK

- [fragapi on PyPI](https://pypi.org/project/fragapi/): official async client, \`pip install fragapi\`, Python 3.10+.
- [SDK source](https://github.com/apelsynca/fragapi-python): one \`FragAPI\` client with a method per endpoint (\`get_me\`, \`get_stars_recipient\`, \`buy_stars\`, \`buy_stars_bulk\`, \`wait_buy_stars_bulk\`, \`buy_premium\`, \`request_ton_deposit\`, \`list_transactions\`, ...).
- [SDK examples](https://github.com/apelsynca/fragapi-python/tree/main/examples/): runnable scripts for each area.

\`\`\`python
import asyncio

from fragapi import FragAPI


async def main() -> None:
    fragapi = FragAPI(token="YOUR_API_TOKEN")
    me = await fragapi.get_me()
    print(me.balance)
    await fragapi.buy_stars(username="synca", quantity=50)


asyncio.run(main())
\`\`\``;

function link(title: string, url: string) {
  return `[${title.replace(/([[\]])/g, "\\$1")}](${url})`;
}

/**
 * `operations` describes the API pages; without it they are left out, which
 * is what the non-English lists want: the API reference is not translated.
 */
function listTree(
  nodes: Node[],
  lang: string,
  operations: Map<string, OperationRef> | undefined,
  indent = 0,
): string[] {
  const prefix = "  ".repeat(indent);
  const out: string[] = [];

  for (const node of nodes) {
    if (node.type === "page") {
      const page = source.getNodePage(node, lang);
      if (!page) continue;

      const operationId = pageOperationId(page);
      if (operationId && !operations) continue;
      const operation = operationId ? operations?.get(operationId) : undefined;
      const description = operation
        ? operationSummary(operation)
        : (page.data.description ?? "");
      const item = `${prefix}- ${link(page.data.title, pageMarkdownUrl(page))}`;
      out.push(description ? `${item}: ${description}` : item);
    } else if (node.type === "folder") {
      const children = node.index
        ? [node.index, ...node.children]
        : node.children;
      const items = listTree(children, lang, operations, indent + 1);
      if (items.length === 0) continue;
      out.push(
        `${prefix}- ${typeof node.name === "string" ? node.name : ""}`,
        ...items,
      );
    }
  }
  return out;
}

/** `llms.txt`: what the service is, plus a link to every page as Markdown. */
export async function buildLLMsIndex() {
  const { operations } = await loadOperations();
  const out = [intro];

  for (const lang of llmsLanguages) {
    const tree = source.getPageTree(lang);
    const isMain = lang === llmsLanguages[0];
    out.push(
      `## ${sectionTitle[lang]}`,
      listTree(tree.children, lang, isMain ? operations : undefined).join("\n"),
    );
  }

  out.push(
    "## Optional",
    [
      `- ${link("Full docs in one file (English)", `${siteUrl}/llms-full.txt`)}: every page above, concatenated`,
      `- ${link("Full docs in one file (Russian)", `${siteUrl}/ru/llms-full.txt`)}`,
      `- ${link("OpenAPI spec", `${apiUrl}/openapi.json`)}: machine-readable schema of every endpoint`,
      `- ${link("Dashboard", dashboardUrl)}: balance, API tokens, transactions`,
      `- ${link("Source code", "https://github.com/apelsynca/fragapi")}: the service itself, open source`,
      `- ${link("Telegram channel", "https://t.me/frag_api")}: news and important notifications`,
      `- ${link("Telegram chat", "https://t.me/fragapichat")}: questions and ideas`,
    ].join("\n"),
  );

  return out.join("\n\n") + "\n";
}

/** `llms-full.txt`: the intro and every page of one language in one file. */
export async function buildLLMsFull(lang: string) {
  // Guides first, then the API reference, in sidebar order.
  const pages = source.getPages(lang);
  const order = new Map<string, number>();
  const visit = (nodes: Node[]) => {
    for (const node of nodes) {
      if (node.type === "page") order.set(node.url, order.size);
      else if (node.type === "folder") {
        if (node.index) order.set(node.index.url, order.size);
        visit(node.children);
      }
    }
  };
  visit(source.getPageTree(lang).children);
  pages.sort(
    (a, b) => (order.get(a.url) ?? Infinity) - (order.get(b.url) ?? Infinity),
  );

  const texts = await Promise.all(pages.map(getLLMText));
  return [intro, ...texts].join("\n\n---\n\n") + "\n";
}

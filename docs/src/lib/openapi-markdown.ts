import { openapiUrl } from "./openapi";

/**
 * Renders OpenAPI operations as Markdown, so the generated API pages (which
 * are an empty React component in MDX) have real content in `llms-full.txt`
 * and the `.md` routes.
 */

type Schema = {
  $ref?: string;
  type?: string | string[];
  format?: string;
  title?: string;
  description?: string;
  enum?: unknown[];
  const?: unknown;
  default?: unknown;
  examples?: unknown[];
  example?: unknown;
  items?: Schema;
  properties?: Record<string, Schema>;
  required?: string[];
  anyOf?: Schema[];
  oneOf?: Schema[];
  allOf?: Schema[];
  minimum?: number;
  maximum?: number;
  exclusiveMinimum?: number;
  exclusiveMaximum?: number;
  minLength?: number;
  maxLength?: number;
  minItems?: number;
  maxItems?: number;
  readOnly?: boolean;
};

type Parameter = {
  name: string;
  in: string;
  required?: boolean;
  description?: string;
  schema?: Schema;
};

type Content = Record<string, { schema?: Schema }>;

type Operation = {
  operationId?: string;
  summary?: string;
  description?: string;
  parameters?: Parameter[];
  requestBody?: { required?: boolean; content?: Content };
  responses?: Record<string, { description?: string; content?: Content }>;
  security?: Record<string, string[]>[];
};

type Document = {
  servers?: { url: string }[];
  paths?: Record<string, Record<string, Operation>>;
  components?: { schemas?: Record<string, Schema> };
};

export type OperationRef = {
  method: string;
  path: string;
  operation: Operation;
};

const METHODS = ["get", "post", "put", "patch", "delete"];
const MAX_DEPTH = 4;

let cached: Promise<Document> | undefined;

function loadDocument(): Promise<Document> {
  cached ??= fetch(openapiUrl).then((res) => {
    if (!res.ok) throw new Error(`OpenAPI spec responded ${res.status}`);
    return res.json() as Promise<Document>;
  });
  // A failed load must not be cached forever.
  cached.catch(() => {
    cached = undefined;
  });
  return cached;
}

/** Operations keyed by `operationId`, or an empty map if the spec is unreachable. */
export async function loadOperations(): Promise<{
  doc: Document;
  operations: Map<string, OperationRef>;
}> {
  const operations = new Map<string, OperationRef>();
  let doc: Document;
  try {
    doc = await loadDocument();
  } catch {
    return { doc: {}, operations };
  }

  for (const [path, item] of Object.entries(doc.paths ?? {})) {
    for (const method of METHODS) {
      const operation = item[method];
      if (operation?.operationId) {
        operations.set(operation.operationId, { method, path, operation });
      }
    }
  }
  return { doc, operations };
}

function refName(ref: string) {
  return ref.slice(ref.lastIndexOf("/") + 1);
}

function resolve(doc: Document, schema: Schema | undefined): Schema {
  if (!schema) return {};
  if (!schema.$ref) return schema;
  return doc.components?.schemas?.[refName(schema.$ref)] ?? {};
}

function variants(schema: Schema) {
  return schema.anyOf ?? schema.oneOf;
}

function typeName(doc: Document, schema: Schema | undefined): string {
  if (!schema) return "any";
  if (schema.$ref) {
    const target = resolve(doc, schema);
    // Enums read better inline than as a bare schema name.
    return target.enum ? typeName(doc, target) : refName(schema.$ref);
  }
  if (schema.enum) return schema.enum.map((v) => JSON.stringify(v)).join(" | ");
  if (schema.const !== undefined) return JSON.stringify(schema.const);

  const options = variants(schema);
  if (options) return options.map((s) => typeName(doc, s)).join(" | ");
  if (schema.allOf)
    return schema.allOf.map((s) => typeName(doc, s)).join(" & ");

  if (schema.type === "array") {
    const item = typeName(doc, schema.items);
    return item.includes(" ") ? `(${item})[]` : `${item}[]`;
  }
  const type = Array.isArray(schema.type)
    ? schema.type.join(" | ")
    : (schema.type ?? "any");
  return schema.format ? `${type} (${schema.format})` : type;
}

function constraints(schema: Schema): string[] {
  const out: string[] = [];
  if (schema.minimum !== undefined) out.push(`min ${schema.minimum}`);
  if (schema.exclusiveMinimum !== undefined)
    out.push(`> ${schema.exclusiveMinimum}`);
  if (schema.maximum !== undefined) out.push(`max ${schema.maximum}`);
  if (schema.exclusiveMaximum !== undefined)
    out.push(`< ${schema.exclusiveMaximum}`);
  if (schema.minLength !== undefined)
    out.push(`min length ${schema.minLength}`);
  if (schema.maxLength !== undefined)
    out.push(`max length ${schema.maxLength}`);
  if (schema.minItems !== undefined) out.push(`min items ${schema.minItems}`);
  if (schema.maxItems !== undefined) out.push(`max items ${schema.maxItems}`);
  if (schema.default !== undefined)
    out.push(`default ${JSON.stringify(schema.default)}`);
  return out;
}

/** The object schema whose fields are worth listing under a field, if any. */
function nestedObject(doc: Document, schema: Schema): Schema | undefined {
  const target = resolve(doc, schema);
  if (target.properties) return target;
  if (target.type === "array") return nestedObject(doc, target.items ?? {});
  for (const option of variants(target) ?? target.allOf ?? []) {
    const found = nestedObject(doc, option);
    if (found) return found;
  }
  return undefined;
}

function fieldLine(
  doc: Document,
  name: string,
  schema: Schema,
  required: boolean,
  indent: number,
) {
  const target = resolve(doc, schema);
  const meta = [
    typeName(doc, schema),
    required ? "required" : "optional",
    ...constraints(target),
  ];
  const description = (schema.description ?? target.description ?? "")
    .replace(/\s+/g, " ")
    .trim();
  const line = `${"  ".repeat(indent)}- \`${name}\` (${meta.join(", ")})`;
  return description ? `${line}: ${description}` : line;
}

function fieldLines(
  doc: Document,
  schema: Schema,
  indent = 0,
  seen: Schema[] = [],
): string[] {
  const object = nestedObject(doc, schema);
  if (!object?.properties || seen.includes(object) || indent >= MAX_DEPTH)
    return [];

  const out: string[] = [];
  for (const [name, property] of Object.entries(object.properties)) {
    out.push(
      fieldLine(
        doc,
        name,
        property,
        object.required?.includes(name) ?? false,
        indent,
      ),
    );
    out.push(...fieldLines(doc, property, indent + 1, [...seen, object]));
  }
  return out;
}

function exampleValue(
  doc: Document,
  schema: Schema | undefined,
  depth = 0,
): unknown {
  const target = resolve(doc, schema);
  if (target.examples?.length) return target.examples[0];
  if (target.example !== undefined) return target.example;
  if (target.default !== undefined) return target.default;
  if (target.const !== undefined) return target.const;
  if (target.enum?.length) return target.enum[0];

  const options = variants(target) ?? target.allOf;
  if (options?.length) {
    const option =
      options.find((s) => resolve(doc, s).type !== "null") ?? options[0];
    return exampleValue(doc, option, depth);
  }

  if (target.properties) {
    if (depth >= MAX_DEPTH) return {};
    return Object.fromEntries(
      Object.entries(target.properties)
        .filter(([, property]) => !resolve(doc, property).readOnly)
        .map(([name, property]) => [
          name,
          exampleValue(doc, property, depth + 1),
        ]),
    );
  }

  switch (Array.isArray(target.type) ? target.type[0] : target.type) {
    case "array":
      return depth >= MAX_DEPTH
        ? []
        : [exampleValue(doc, target.items, depth + 1)];
    case "integer":
    case "number":
      return target.minimum ?? 1;
    case "boolean":
      return false;
    case "string":
      return "string";
    default:
      return null;
  }
}

function jsonSchema(content: Content | undefined) {
  return content?.["application/json"]?.schema;
}

/** API tokens never carry the `web` scope: those endpoints are for the dashboard. */
function isDashboardOnly(operation: Operation) {
  const scopes = (operation.security ?? []).flatMap((r) => r.api_token ?? []);
  return scopes.length > 0 && scopes.every((scope) => scope === "web");
}

function authLine(operation: Operation) {
  if (!operation.security?.length) return "Authorization: none.";
  if (isDashboardOnly(operation))
    return "Authorization: dashboard session only. API tokens get `401` here.";
  return "Authorization: `Authorization: Bearer <API token>`.";
}

function curlExample(doc: Document, { method, path, operation }: OperationRef) {
  const base = doc.servers?.[0]?.url ?? "https://api.fragapi.com";
  const query = (operation.parameters ?? [])
    .filter((p) => p.in === "query" && p.required)
    .map((p) => `${p.name}=${String(exampleValue(doc, p.schema))}`)
    .join("&");
  const url =
    base + path.replace(/\{(\w+)\}/g, "<$1>") + (query ? `?${query}` : "");
  const lines = [`curl -X ${method.toUpperCase()} "${url}" \\`];
  const body = jsonSchema(operation.requestBody?.content);

  lines.push(`  -H "Authorization: Bearer $FRAGAPI_TOKEN"${body ? " \\" : ""}`);
  if (body) {
    lines.push(
      '  -H "Content-Type: application/json" \\',
      `  -d '${JSON.stringify(exampleValue(doc, body))}'`,
    );
  }
  return ["```bash", ...lines, "```"].join("\n");
}

export function operationSummary({ method, path, operation }: OperationRef) {
  const description = (operation.description ?? "").split("\n")[0].trim();
  const signature = `\`${method.toUpperCase()} ${path}\``;
  const note = isDashboardOnly(operation) ? " (dashboard session only)" : "";
  return (description ? `${signature} — ${description}` : signature) + note;
}

export function renderOperation(doc: Document, ref: OperationRef): string {
  const { method, path, operation } = ref;
  const out: string[] = [`\`${method.toUpperCase()} ${path}\``];

  if (operation.description) out.push(operation.description.trim());
  out.push(authLine(operation));

  for (const [place, title] of [
    ["path", "Path parameters"],
    ["query", "Query parameters"],
    ["header", "Header parameters"],
  ]) {
    const parameters = (operation.parameters ?? []).filter(
      (p) => p.in === place,
    );
    if (parameters.length === 0) continue;
    out.push(
      `## ${title}`,
      parameters
        .map((p) =>
          fieldLine(
            doc,
            p.name,
            {
              ...p.schema,
              description: p.description ?? p.schema?.description,
            },
            p.required ?? false,
            0,
          ),
        )
        .join("\n"),
    );
  }

  const body = jsonSchema(operation.requestBody?.content);
  if (body) {
    const fields = fieldLines(doc, body);
    out.push(
      "## Request body",
      `JSON, \`${typeName(doc, body)}\`:`,
      ...(fields.length ? [fields.join("\n")] : []),
    );
  }

  const responses = Object.entries(operation.responses ?? {});
  if (responses.length > 0) {
    out.push("## Responses");
    for (const [status, response] of responses) {
      const schema = jsonSchema(response.content);
      const type = schema ? ` — \`${typeName(doc, schema)}\`` : "";
      out.push(`**${status}** ${response.description ?? ""}${type}`.trim());

      // Error bodies share one shape; only spell out the success payload.
      if (schema && status.startsWith("2")) {
        const fields = fieldLines(doc, schema);
        if (fields.length) out.push(fields.join("\n"));
      }
    }
  }

  out.push("## Example", curlExample(doc, ref));
  return out.join("\n\n");
}

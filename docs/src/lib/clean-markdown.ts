import { siteUrl } from "./site";

/**
 * Turns the processed MDX of a guide page into plain Markdown: the JSX that
 * only makes sense in the browser (cards, tabs, accordions, the banner) is
 * dropped or rewritten, so `.md` routes and `llms-full.txt` read cleanly.
 */

const attr = (tag: string, name: string) =>
  new RegExp(`\\s${name}="([^"]*)"`).exec(tag)?.[1];

/** `<PythonIcon /> example.py` -> `example.py` */
const stripIcons = (text: string) => text.replace(/<\w+\s*\/>/g, "").trim();

function inline(line: string) {
  return line
    .replace(/<\/?b>/g, "**")
    .replace(/<\/?i>/g, "*")
    .replace(/\{\/\*.*?\*\/\}/g, "")
    .replace(/^(#{1,6} .*?)\s+\[#[^\]]*\]$/, "$1")
    .replace(/\]\(\/(?!\/)/g, `](${siteUrl}/`);
}

export function cleanMarkdown(text: string): string {
  const out: string[] = [];
  let fenceIndent: number | undefined;
  let skipUntil: string | undefined;
  let card: { title: string; href: string; text: string[] } | undefined;
  let quote = false;

  for (const raw of text.split("\n")) {
    const line = raw.trimStart();
    const indent = raw.length - line.length;

    // Code is copied as is, minus the indentation of the JSX around it.
    if (fenceIndent !== undefined) {
      out.push(raw.slice(Math.min(indent, fenceIndent)));
      if (line.startsWith("```")) fenceIndent = undefined;
      continue;
    }
    if (line.startsWith("```")) {
      fenceIndent = indent;
      out.push(line);
      continue;
    }

    if (skipUntil) {
      if (line.startsWith(skipUntil)) skipUntil = undefined;
      continue;
    }
    // The tab buttons repeat the labels of the tabs below them.
    if (line.startsWith("<CodeBlockTabsList")) {
      skipUntil = "</CodeBlockTabsList>";
      continue;
    }

    if (card) {
      if (line.startsWith("</Card>")) {
        const description = card.text.join(" ");
        const item = `- [${card.title}](${card.href})`;
        out.push(description ? `${item}: ${description}` : item);
        card = undefined;
      } else if (line) {
        card.text.push(inline(line));
      }
      continue;
    }
    if (line.startsWith("<Card ")) {
      card = {
        title: attr(line, "title") ?? "",
        href: attr(line, "href") ?? "",
        text: [],
      };
      continue;
    }

    if (line.startsWith("<CodeBlockTab ")) {
      const label = stripIcons(attr(line, "value") ?? "");
      if (label) out.push(`\`${label}\`:`, "");
      continue;
    }
    if (line.startsWith("<Accordion ")) {
      const title = attr(line, "title");
      if (title) out.push(`**${title}**`, "");
      continue;
    }
    if (line.startsWith("<Callout")) {
      quote = true;
      continue;
    }
    if (line.startsWith("</Callout>")) {
      quote = false;
      continue;
    }

    // Any other line that is only a tag: layout wrappers, images, icons.
    if (/^<\/?[A-Za-z][\w.]*(\s[^]*)?>$/.test(line) && !/^<(b|i)>/.test(line))
      continue;

    const cleaned = inline(line);
    out.push(quote && cleaned ? `> ${cleaned}` : cleaned);
  }

  return out
    .join("\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

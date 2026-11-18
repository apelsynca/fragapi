import { createFileRoute } from '@tanstack/react-router';
import { markdownHeaders, notFoundResponse } from '@/lib/llms';
import { getLLMText, markdownPathToSlugs, source } from '@/lib/source';

export const Route = createFileRoute('/$lang/docs/{$}.md')({
  server: {
    handlers: {
      GET: async ({ params }) => {
        const slugs = markdownPathToSlugs(params._splat?.split('/') ?? []);
        const page = source.getPage(slugs, params.lang);
        if (!page) return notFoundResponse();

        return new Response(await getLLMText(page), {
          headers: markdownHeaders,
        });
      },
    },
  },
});

import {
  buildLLMsFull,
  isDocsLanguage,
  markdownHeaders,
  notFoundResponse,
} from '@/lib/llms';
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/$lang/llms-full.txt')({
  server: {
    handlers: {
      GET: async ({ params }) => {
        if (!isDocsLanguage(params.lang)) return notFoundResponse();

        return new Response(await buildLLMsFull(params.lang), {
          headers: markdownHeaders,
        });
      },
    },
  },
});

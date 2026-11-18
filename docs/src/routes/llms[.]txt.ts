import { buildLLMsIndex, markdownHeaders } from '@/lib/llms';
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/llms.txt')({
  server: {
    handlers: {
      GET: async () =>
        new Response(await buildLLMsIndex(), { headers: markdownHeaders }),
    },
  },
});

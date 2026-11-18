import { buildLLMsFull, markdownHeaders } from '@/lib/llms';
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/llms-full.txt')({
  server: {
    handlers: {
      GET: async () =>
        new Response(await buildLLMsFull('en'), { headers: markdownHeaders }),
    },
  },
});

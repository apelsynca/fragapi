import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 15, // 15 seconds
      gcTime: 1000 * 60 * 15, // 15 minutes
    },
  },
})

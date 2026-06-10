import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // With SSR, we usually want to set some default staleTime
      // above 0 to avoid refetching immediately on the client
      staleTime: 1000 * 30, // 30 seconds
      // gcTime needs to be _higher_ than maxAge in any persisted clients
      // see https://tanstack.com/query/v5/docs/react/plugins/persistQueryClient
      gcTime: 1000 * 60 * 15, // 15 minutes
    },
  },
})

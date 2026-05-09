import { createFileRoute } from '@tanstack/react-router'
import DashboardStats from '~/components/DashboardStats'
import DashboardChart from '~/components/DashboardChart'
import {
  fetchATransactionsChart,
  fetchATransactionStats,
} from '~/lib/different'

export const Route = createFileRoute('/_authed/dashboard/')({
  component: RouteComponent,
  loader: async ({ context }) => {
    await context.queryClient.prefetchQuery({
      queryKey: ['transactions', 'stats'],
      queryFn: () => fetchATransactionStats(),
    })
    await context.queryClient.prefetchQuery({
      queryKey: ['transactions', 'chart'],
      queryFn: () => fetchATransactionsChart(),
    })
  },
})

function RouteComponent() {
  return (
    <div className="flex flex-col gap-1 md:gap-2.5">
      <DashboardStats />
      <DashboardChart />
    </div>
  )
}

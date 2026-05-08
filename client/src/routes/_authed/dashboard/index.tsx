import { createFileRoute } from '@tanstack/react-router'
import DashboardStats from '#/components/DashboardStats'
import DashboardChart from '#/components/DashboardChart'
import {
  tonRateQueryOptions,
  transactionChartOptions,
  transactionStatsOptions,
} from '#/lib/queries'

export const Route = createFileRoute('/_authed/dashboard/')({
  component: RouteComponent,
  loader: async ({ context }) => {
    await Promise.all([
      context.queryClient.ensureQueryData(tonRateQueryOptions()),
      context.queryClient.ensureQueryData(transactionStatsOptions()),
      context.queryClient.ensureQueryData(transactionChartOptions()),
    ])
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

import { createFileRoute } from '@tanstack/react-router'
import { fetchMe } from '#/lib/user'
import DashboardStats from '#/components/DashboardStats'
import DashboardChart from '#/components/DashboardChart'

export const Route = createFileRoute('/_authed/dashboard/')({
  component: RouteComponent,
  loader: async () => {
    return await fetchMe()
  },
})

function RouteComponent() {
  const user = Route.useLoaderData()

  return (
    <div className="flex flex-col gap-1 md:gap-2.5">
      <DashboardStats userBalance={user.balance} />
      <DashboardChart />
    </div>
  )
}

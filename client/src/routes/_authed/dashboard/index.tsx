import { createFileRoute } from '@tanstack/react-router'
import { fetchMe } from '#/lib/user'
import DashboardStats from '#/components/DashboardStats'

export const Route = createFileRoute('/_authed/dashboard/')({
  component: RouteComponent,
  loader: async () => {
    return await fetchMe()
  },
})

function RouteComponent() {
  const user = Route.useLoaderData()

  return (
    <div className="">
      <DashboardStats userBalance={2.52} />
    </div>
  )
}

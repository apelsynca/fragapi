import { createFileRoute } from '@tanstack/react-router'
import { fetchMe } from '~/server/user'

export const Route = createFileRoute('/dashboard/')({
  component: RouteComponent,
  loader: async () => {
    return {
      user: await fetchMe(),
    }
  },
})

function RouteComponent() {
  const { user } = Route.useLoaderData()

  return (
    <div className="flex flex-col gap-1 md:gap-2.5">
      Hello, world! balance = {user.balance} TON
      <div>(Секретный ключ: {user.apiKey}) </div>
    </div>
  )
}

// <Suspense fallback={<div>FALLBACK STATS</div>}>
//   <DashboardStats />
// </Suspense>
// <Suspense fallback={<div>FALLBACK CHART</div>}>
//   <DashboardChart />
// </Suspense>

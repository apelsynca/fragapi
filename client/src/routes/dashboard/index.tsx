import { createFileRoute } from '@tanstack/react-router'
import { Card, CardContent, CardHeader, CardTitle } from '~/components/ui/card'
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
      <Card>
        <CardHeader>
          <CardTitle>Ваш баланс</CardTitle>
        </CardHeader>
        <CardContent className="font-semibold text-lg">
          {parseFloat(user.balance.toFixed(2))} TON
        </CardContent>
      </Card>
    </div>
  )
}

// <Suspense fallback={<div>FALLBACK STATS</div>}>
//   <DashboardStats />
// </Suspense>
// <Suspense fallback={<div>FALLBACK CHART</div>}>
//   <DashboardChart />
// </Suspense>

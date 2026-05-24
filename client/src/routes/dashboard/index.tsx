import { createFileRoute } from '@tanstack/react-router'
import { Suspense } from 'react'
import DashboardChart from '~/components/DashboardChart'
import DashboardStats from '~/components/DashboardStats'

export const Route = createFileRoute('/dashboard/')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div className="flex flex-col gap-1 md:gap-2.5">
      <Suspense fallback={<p>Loading..</p>}>
        <DashboardStats />
      </Suspense>
      <Suspense fallback={<p>Loading...</p>}>
        <DashboardChart />
      </Suspense>
    </div>
  )
}

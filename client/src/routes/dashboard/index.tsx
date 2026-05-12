import { Suspense } from 'react'
import { createFileRoute } from '@tanstack/react-router'
import DashboardStats from '~/components/DashboardStats'
import DashboardChart from '~/components/DashboardChart'

export const Route = createFileRoute('/dashboard/')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div className="flex flex-col gap-1 md:gap-2.5">
      <Suspense fallback={<div>FALLBACK STATS</div>}>
        <DashboardStats />
      </Suspense>
      <Suspense fallback={<div>FALLBACK CHART</div>}>
        <DashboardChart />
      </Suspense>
    </div>
  )
}

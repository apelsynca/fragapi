import { createFileRoute } from '@tanstack/react-router'
import { Suspense } from 'react'
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
    </div>
  )
}

// <Suspense fallback={<div>FALLBACK STATS</div>}>
//   <DashboardStats />
// </Suspense>
// <Suspense fallback={<div>FALLBACK CHART</div>}>
//   <DashboardChart />
// </Suspense>

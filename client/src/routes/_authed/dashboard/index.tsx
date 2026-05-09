import { createFileRoute } from '@tanstack/react-router'
import DashboardStats from '~/components/DashboardStats'
import DashboardChart from '~/components/DashboardChart'
import { Suspense } from 'react'

export const Route = createFileRoute('/_authed/dashboard/')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div className="flex flex-col gap-1 md:gap-2.5">
      <Suspense>
        <DashboardStats />
      </Suspense>
      <Suspense>
        <DashboardChart />
      </Suspense>
    </div>
  )
}

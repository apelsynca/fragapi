import { Suspense } from 'react'
import DashboardChart from '~/components/Dashboard/DashboardChart'
import DashboardStats from '~/components/Dashboard/DashboardStats'

export default function Dashboard({ className }: { className?: string }) {
  return (
    <div className={className}>
      <Suspense fallback={<p>Loading..</p>}>
        <DashboardStats />
      </Suspense>
      <Suspense fallback={<p>Loading...</p>}>
        <DashboardChart />
      </Suspense>
    </div>
  )
}

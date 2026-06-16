import { Suspense } from 'react'
import DashboardChart from '#/components/Dashboard/DashboardChart'
import DashboardStats from '#/components/Dashboard/DashboardStats'
import DashboardChartSkeleton from './DashboardChartSkeleton'
import DashboardStatsSkeleton from './DashboardStatsSkeleton'

export default function Dashboard({ className }: { className?: string }) {
  return (
    <div className={className}>
      <Suspense fallback={<DashboardStatsSkeleton />}>
        <DashboardStats />
      </Suspense>
      <Suspense fallback={<DashboardChartSkeleton />}>
        <DashboardChart />
      </Suspense>
    </div>
  )
}

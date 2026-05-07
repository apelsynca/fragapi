import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import DashboardStatsCard from './DashboardStatsCard'
import { fetchTransactionStats } from '#/lib/transactions'
import { tonRateQueryOptions } from '#/lib/fragment'

interface DashboardStatsProps {
  userBalance: number
}

export default function DashboardStats({ userBalance }: DashboardStatsProps) {
  const { data } = useQuery({
    queryKey: ['transactions', 'stats'],
    queryFn: () => fetchTransactionStats(),
  })
  const { data: tonRate } = useQuery(tonRateQueryOptions())

  const transactionStats = useMemo(() => {
    return data === undefined
      ? {
          starsPurchasesCount: 0,
          premiumCount: 0,
          totalSpent: 0,
        }
      : data
  }, [data])

  return (
    <div className="flex flex-col items-center md:grid md:grid-cols-4 gap-1 md:gap-2.5">
      <DashboardStatsCard
        description="Баланс"
        amount={userBalance}
        fiatAmount={userBalance * (tonRate || 0)}
      />
      <DashboardStatsCard
        description="Общие траты"
        amount={transactionStats.totalSpent}
        fiatAmount={transactionStats.totalSpent * (tonRate || 0)}
        percent={15.2}
      />
      <DashboardStatsCard
        description="Траты на звезды"
        amount={transactionStats.starsPurchasesCount}
        fiatAmount={0 * (tonRate || 0)}
        percent={52.2}
      />
      <DashboardStatsCard
        description="Траты на премиум"
        amount={transactionStats.premiumCount}
        fiatAmount={0 * (tonRate || 0)}
        percent={-3.3}
      />
    </div>
  )
}

import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import DashboardStatsCard from './DashboardStatsCard'
import { tonRateQueryOptions } from '#/lib/fragment'
import { transactionStatsOptions } from '#/lib/transactions'
import { userMeQueryOptions } from '#/lib/user'

export default function DashboardStats() {
  const { data: user } = useQuery(userMeQueryOptions())
  const { data } = useQuery(transactionStatsOptions())
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
        amount={user ? user.balance : 0}
        fiatAmount={user ? user.balance * (tonRate || 0) : 0}
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

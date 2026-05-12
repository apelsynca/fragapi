import { useSuspenseQuery } from '@tanstack/react-query'
import DashboardStatsCard from './DashboardStatsCard'
import BalanceTopUp from './BalanceTopUp'
import {
  tonRateQueryOptions,
  transactionStatsOptions,
  userMeQueryOptions,
} from '~/lib/queries'

export default function DashboardStats() {
  const { data: user } = useSuspenseQuery(userMeQueryOptions())
  const { data: transactionStats } = useSuspenseQuery(transactionStatsOptions())
  const { data: tonRate } = useSuspenseQuery(tonRateQueryOptions())

  return (
    <div className="flex flex-col items-center md:grid md:grid-cols-4 gap-1 md:gap-2.5">
      <DashboardStatsCard
        name="Баланс"
        amount={user.balance}
        fiatAmount={user.balance * tonRate}
        after={<BalanceTopUp />}
      />
      <DashboardStatsCard
        name="Общие траты"
        amount={transactionStats.monthlySpend || 0}
        fiatAmount={transactionStats.totalSpent * tonRate}
        percent={0}
        description="За последние 30 дней"
      />
      <DashboardStatsCard
        name="Траты на звезды"
        amount={transactionStats.starsMonthlySpend || 0}
        fiatAmount={transactionStats.starsMonthlySpend * tonRate}
        percent={0}
        description="За последние 30 дней"
      />
      <DashboardStatsCard
        name="Траты на премиум"
        amount={transactionStats.premiumMonthlySpend || 0}
        fiatAmount={transactionStats.premiumMonthlySpend * tonRate}
        percent={0}
        description="За последние 30 дней"
      />
    </div>
  )
}

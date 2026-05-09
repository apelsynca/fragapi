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
        fiatAmount={user.balance * (tonRate || 0)}
        after={<BalanceTopUp />}
      />
      <DashboardStatsCard
        name="Общие траты"
        amount={transactionStats.totalSpent}
        fiatAmount={transactionStats.totalSpent * (tonRate || 0)}
        percent={15.2}
        description="За последние 30 дней"
      />
      <DashboardStatsCard
        name="Траты на звезды"
        amount={transactionStats.starsPurchasesCount}
        fiatAmount={0 * (tonRate || 0)}
        percent={52.2}
        description="За последние 30 дней"
      />
      <DashboardStatsCard
        name="Траты на премиум"
        amount={transactionStats.premiumCount}
        fiatAmount={0 * (tonRate || 0)}
        percent={-3.3}
        description="За последние 30 дней"
      />
    </div>
  )
}

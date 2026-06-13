import { useSuspenseQuery } from '@tanstack/react-query'
import DashboardStatsCard from './DashboardStatsCard'
import BalanceTopUp from '#/components/BalanceTopUp'
import {
  tonRateOptions,
  transactionsStatsOptions,
  userMeOptions,
} from '#/lib/queries'
import { m } from '#/paraglide/messages'

export default function DashboardStats() {
  const { data: user } = useSuspenseQuery(userMeOptions())
  const { data: tonRate } = useSuspenseQuery(tonRateOptions())
  const { data: transactionStats } = useSuspenseQuery(
    transactionsStatsOptions(),
  )

  return (
    <div className="flex flex-col items-center md:grid md:grid-cols-4 gap-1.5 md:gap-2.5">
      <DashboardStatsCard
        name={m.stats_balance()}
        amount={user.balance}
        fiatAmount={user.balance * tonRate}
        after={<BalanceTopUp />}
      />
      <DashboardStatsCard
        name={m.stats_spend()}
        amount={transactionStats.totalSpend || 0}
        fiatAmount={transactionStats.totalSpend * tonRate}
        percent={0}
        description={m.stats_all_time()}
      />
      <DashboardStatsCard
        name={m.stats_stars_spend()}
        amount={transactionStats.starsTotalSpend || 0}
        fiatAmount={transactionStats.starsTotalSpend * tonRate}
        percent={0}
        description={m.stats_all_time()}
      />
      <DashboardStatsCard
        name={m.stats_premium_spend()}
        amount={transactionStats.premiumTotalSpend || 0}
        fiatAmount={transactionStats.premiumTotalSpend * tonRate}
        percent={0}
        description={m.stats_all_time()}
      />
    </div>
  )
}

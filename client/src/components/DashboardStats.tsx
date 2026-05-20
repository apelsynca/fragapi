import { useSuspenseQuery } from '@tanstack/react-query'
import DashboardStatsCard from './DashboardStatsCard'
import BalanceTopUp from './BalanceTopUp'
import {
  tonRateQueryOptions,
  transactionsStatsQueryOptions,
  userMeQueryOptions,
} from '~/lib/queries'
import { useTranslation } from 'react-i18next'

export default function DashboardStats() {
  const { t } = useTranslation()

  const { data: user } = useSuspenseQuery(userMeQueryOptions())
  const { data: tonRate } = useSuspenseQuery(tonRateQueryOptions())
  const { data: transactionStats } = useSuspenseQuery(
    transactionsStatsQueryOptions(),
  )

  return (
    <div className="flex flex-col items-center md:grid md:grid-cols-4 gap-1 md:gap-2.5">
      <DashboardStatsCard
        name={t('stats.balance')}
        amount={user.balance}
        fiatAmount={user.balance * tonRate}
        after={<BalanceTopUp />}
      />
      <DashboardStatsCard
        name={t('stats.spend')}
        amount={transactionStats.totalSpend || 0}
        fiatAmount={transactionStats.totalSpend * tonRate}
        percent={0}
        description={t('stats.all_time')}
      />
      <DashboardStatsCard
        name={t('stats.stars_spend')}
        amount={transactionStats.starsTotalSpend || 0}
        fiatAmount={transactionStats.starsTotalSpend * tonRate}
        percent={0}
        description={t('stats.all_time')}
      />
      <DashboardStatsCard
        name={t('stats.premium_spend')}
        amount={transactionStats.premiumTotalSpend || 0}
        fiatAmount={transactionStats.premiumTotalSpend * tonRate}
        percent={0}
        description={t('stats.all_time')}
      />
    </div>
  )
}

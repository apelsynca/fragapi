import { useSuspenseQuery } from '@tanstack/react-query'
import DashboardStatsCard from './DashboardStatsCard'
import BalanceTopUp from './BalanceTopUp'
import { tonRateQueryOptions, userMeQueryOptions } from '~/lib/queries'
import { useTranslation } from 'react-i18next'

export default function DashboardStats() {
  const { t } = useTranslation()

  const { data: user } = useSuspenseQuery(userMeQueryOptions())
  const { data: tonRate } = useSuspenseQuery(tonRateQueryOptions())

  return (
    <div className="flex flex-col items-center md:grid md:grid-cols-4 gap-1 md:gap-2.5">
      <DashboardStatsCard
        name={t('stats.balance')}
        amount={user.balance}
        fiatAmount={user.balance * tonRate}
        after={<BalanceTopUp />}
      />
    </div>
  )
}

// <DashboardStatsCard
//   name={t('stats.spend')}
//   amount={transactionStats.monthlySpend || 0}
//   fiatAmount={transactionStats.totalSpent * tonRate}
//   percent={0}
//   description={t('stats.last_30days')}
// />
// <DashboardStatsCard
//   name={t('stats.stars_spend')}
//   amount={transactionStats.starsMonthlySpend || 0}
//   fiatAmount={transactionStats.starsMonthlySpend * tonRate}
//   percent={0}
//   description={t('stats.last_30days')}
// />
// <DashboardStatsCard
//   name={t('stats.premium_spend')}
//   amount={transactionStats.premiumMonthlySpend || 0}
//   fiatAmount={transactionStats.premiumMonthlySpend * tonRate}
//   percent={0}
//   description={t('stats.last_30days')}
// />

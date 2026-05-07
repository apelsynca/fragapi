import DashboardStatsCard from './DashboardStatsCard'

interface DashboardStatsProps {
  userBalance: number
}

export default function DashboardStats({ userBalance }: DashboardStatsProps) {
  return (
    <div className="flex flex-col items-center md:grid md:grid-cols-4 gap-1 md:gap-2.5">
      <DashboardStatsCard
        description="Баланс"
        amount={userBalance}
        fiatAmount={2.5}
      />
      <DashboardStatsCard
        description="Общие траты"
        amount={1000}
        fiatAmount={3.62}
        percent={15.2}
      />
      <DashboardStatsCard
        description="Траты на звезды"
        amount={102}
        fiatAmount={3.25}
        percent={52.2}
      />
      <DashboardStatsCard
        description="Траты на премиум"
        amount={52}
        fiatAmount={3}
        percent={-3.3}
      />
    </div>
  )
}

import { TON_RATE } from './demoState'
import type { DemoState } from './demoState'
import { GramIcon } from '#/components/icons/GramIcon'
import { Card } from '#/components/ui/card'
import { useCountUp } from '#/hooks/useCountUp'
import { m } from '#/paraglide/messages'

/** `useCountUp` eases whole numbers, so amounts are eased in hundredths. */
function useEasedAmount(amount: number) {
  return useCountUp(Math.round(amount * 100), 700) / 100
}

function StatTile({
  name,
  amount,
  children,
}: {
  name: string
  amount: number
  children: React.ReactNode
}) {
  const shown = useEasedAmount(amount)

  return (
    <Card className="gap-2 px-4">
      <p className="text-muted-foreground truncate">{name}</p>
      <div>
        <p className="flex items-center gap-1.5 text-2xl font-semibold tabular-nums">
          {shown.toFixed(2)} <GramIcon size={20} />
        </p>
        <p className="text-muted-foreground font-medium tabular-nums">
          ~${(shown * TON_RATE).toFixed(2)}
        </p>
      </div>
      {children}
    </Card>
  )
}

/** Compact take on `DashboardStats`, sized for the hero window. */
export default function DemoStats({ state }: { state: DemoState }) {
  const allTime = (
    <p className="text-muted-foreground truncate">{m.stats_all_time()}</p>
  )

  return (
    <div
      aria-hidden
      className="grid shrink-0 grid-cols-2 gap-2.5 xl:grid-cols-4"
    >
      <StatTile name={m.stats_balance()} amount={state.balance}>
        <span className="bg-primary text-primary-foreground truncate rounded-md px-2 py-0.5 text-center text-xs leading-4 font-medium">
          {m.deposit()}
        </span>
      </StatTile>
      <StatTile
        name={m.stats_spend()}
        amount={state.starsSpend + state.premiumSpend}
      >
        {allTime}
      </StatTile>
      <StatTile name={m.stats_stars_spend()} amount={state.starsSpend}>
        {allTime}
      </StatTile>
      <StatTile name={m.stats_premium_spend()} amount={state.premiumSpend}>
        {allTime}
      </StatTile>
    </div>
  )
}

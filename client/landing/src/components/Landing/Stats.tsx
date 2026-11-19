import { CrownIcon, StarIcon } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { useCountUp } from '#/hooks/useCountUp'
import { useStatsTotals } from '#/hooks/useStatsTotals'

// Cells draw their own top/left border and the wrapper clips the outer ones,
// so dividers stay right however the grid wraps.
const CELL_DIVIDERS = 'border-border -mt-px -ml-px border-t border-l'

function CounterValue({ value }: { value: number }) {
  const shown = useCountUp(value)

  return <>{new Intl.NumberFormat('ru-RU').format(shown)}</>
}

interface LiveCounterProps {
  icon: LucideIcon
  label: string
  value: number | undefined
}

function LiveCounter({ icon: Icon, label, value }: LiveCounterProps) {
  return (
    <div
      className={`${CELL_DIVIDERS} flex flex-col gap-5 px-6 pt-8 pb-9 sm:px-10`}
    >
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="bg-brand/12 text-brand flex size-10 shrink-0 items-center justify-center rounded-[10px]">
            <Icon className="size-5" />
          </div>
          <p className="font-medium">{label}</p>
        </div>
        <div className="flex items-center gap-1.5 rounded-full bg-green-400/10 py-0.5 pr-2.5 pl-2 text-xs leading-5 font-medium text-green-400">
          <span className="relative flex size-3 items-center justify-center">
            <span className="absolute size-full rounded-full bg-green-400/25 motion-safe:animate-ping" />
            <span className="size-1.5 rounded-full bg-green-400" />
          </span>
          В реальном времени
        </div>
      </div>
      <div className="flex flex-col gap-1">
        <p className="text-5xl leading-20 font-semibold tracking-[-0.03em] tabular-nums sm:text-7xl sm:leading-20">
          {value === undefined ? '—' : <CounterValue value={value} />}
        </p>
        <p className="text-muted-foreground text-sm">
          Через FragAPI за всё время
        </p>
      </div>
    </div>
  )
}

export default function Stats() {
  const { data: totals } = useStatsTotals()

  const strip = [
    { value: '1.8%', label: 'Комиссия в облаке' },
    { value: '0%', label: 'Комиссия при self-hosted' },
    { value: '≈ $0.001', label: 'Сетевая комиссия за транзакцию' },
    { value: 'MIT', label: 'Полностью открытый код' },
  ]

  return (
    // Positioned so it paints over the hero background that bleeds in.
    <section className="relative w-full px-4 pt-16 sm:pt-24">
      <div className="mx-auto flex max-w-280 flex-col gap-4">
        <div className="border-border from-brand/8 grid overflow-hidden rounded-2xl border bg-white/2 bg-linear-to-b to-transparent to-70% md:grid-cols-2">
          <LiveCounter
            icon={StarIcon}
            label="Куплено звёзд"
            value={totals?.starsTotal}
          />
          <LiveCounter
            icon={CrownIcon}
            label="Куплено месяцев Premium"
            value={totals?.premiumMonthsTotal}
          />
        </div>
        <div className="border-border grid overflow-hidden rounded-2xl border bg-white/2 sm:grid-cols-2 lg:grid-cols-4">
          {strip.map((stat) => (
            <div
              key={stat.label}
              className={`${CELL_DIVIDERS} flex flex-col gap-1 py-7 pr-4 pl-8`}
            >
              <p className="text-[32px] leading-10 font-semibold tracking-[-0.02em]">
                {stat.value}
              </p>
              <p className="text-muted-foreground text-sm">{stat.label}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

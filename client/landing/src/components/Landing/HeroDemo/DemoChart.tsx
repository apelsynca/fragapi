import { useId } from 'react'
import { CHART_MAX } from './demoState'
import type { ChartPoint, PurchaseKind } from './demoState'
import { Card } from '#/components/ui/card'

const STEP = 10
const HEIGHT = 100

const SERIES: { kind: PurchaseKind; label: string; color: string }[] = [
  { kind: 'stars', label: 'Stars', color: 'var(--chart-1)' },
  { kind: 'premium', label: 'Premium', color: 'var(--chart-2)' },
]

/** Step line through the points: a flat run per point, as the dashboard draws it. */
function stepLine(chart: ChartPoint[], kind: PurchaseKind) {
  return chart
    .map((point, index) => {
      const y = HEIGHT - (Math.min(point[kind], CHART_MAX) / CHART_MAX) * HEIGHT
      return `${index === 0 ? 'M' : 'L'}${index * STEP},${y} H${(index + 1) * STEP}`
    })
    .join(' ')
}

/**
 * Hand-drawn stand-in for `DashboardChart`, so the landing page does not pull
 * in the charting library.
 */
export default function DemoChart({ chart }: { chart: ChartPoint[] }) {
  const gradientId = useId()
  const width = chart.length * STEP

  return (
    <Card aria-hidden className="hidden shrink-0 gap-0 py-0 xl:flex">
      <div className="border-b px-4 py-3">
        <p className="text-base leading-snug font-medium">
          Статистика транзакций
        </p>
        <p className="text-muted-foreground truncate">
          Показываем транзакции за последние 90 дней
        </p>
      </div>
      <div className="px-4 pt-4 pb-3">
        <svg
          viewBox={`0 0 ${width} ${HEIGHT}`}
          preserveAspectRatio="none"
          className="h-20 w-full overflow-visible"
        >
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="var(--chart-1)" stopOpacity={0.8} />
              <stop offset="95%" stopColor="var(--chart-2)" stopOpacity={0.1} />
            </linearGradient>
          </defs>
          {[0, 0.25, 0.5, 0.75, 1].map((line) => (
            <line
              key={line}
              x1={0}
              x2={width}
              y1={line * HEIGHT}
              y2={line * HEIGHT}
              className="stroke-border"
              vectorEffect="non-scaling-stroke"
            />
          ))}
          {SERIES.map(({ kind, color }) => {
            const line = stepLine(chart, kind)

            return (
              <g key={kind}>
                <path
                  d={`${line} V${HEIGHT} H0 Z`}
                  fill={`url(#${gradientId})`}
                  fillOpacity={0.6}
                />
                <path
                  d={line}
                  fill="none"
                  stroke={color}
                  vectorEffect="non-scaling-stroke"
                />
              </g>
            )
          })}
        </svg>
        <div className="flex justify-center gap-4 pt-3 text-xs">
          {SERIES.toReversed().map(({ kind, label, color }) => (
            <span key={kind} className="flex items-center gap-1.5">
              <span
                className="size-2 rounded-[2px]"
                style={{ backgroundColor: color }}
              />
              {label}
            </span>
          ))}
        </div>
      </div>
    </Card>
  )
}

import { useSuspenseQuery } from '@tanstack/react-query'
import { Area, AreaChart, CartesianGrid, XAxis } from 'recharts'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '#/components/ui/card'
import type { ChartConfig } from '#/components/ui/chart'
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
} from '#/components/ui/chart'
import { transactionChartOptions } from '#/lib/queries'
import { m } from '#/paraglide/messages'

const chartConfig = {
  visitors: {
    label: 'Статистика',
  },
  starsSpend: {
    label: 'Stars',
    color: 'var(--chart-1)',
  },
  premiumSpend: {
    label: 'Premium',
    color: 'var(--chart-2)',
  },
} satisfies ChartConfig

export default function DashboardChart() {
  const { data: chartData } = useSuspenseQuery(transactionChartOptions())

  return (
    <Card className="pt-0">
      <CardHeader className="flex items-center gap-2 space-y-0 border-b py-5 sm:flex-row">
        <div className="grid flex-1 gap-1">
          <CardTitle>{m.stats_transaction_stats()}</CardTitle>
          <CardDescription>{m.stats_90days_chart()}</CardDescription>
        </div>
      </CardHeader>
      <CardContent className="px-2 pt-4 sm:px-6 sm:pt-6">
        <ChartContainer
          config={chartConfig}
          className="aspect-auto h-62.5 w-full"
        >
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="fillStarsSpend" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--color-starsSpend)"
                  stopOpacity={0.8}
                />
                <stop
                  offset="95%"
                  stopColor="var(--color-premiumSpend)"
                  stopOpacity={0.1}
                />
              </linearGradient>
              <linearGradient id="fillPremiumSpend" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--color-starsSpend)"
                  stopOpacity={0.8}
                />
                <stop
                  offset="95%"
                  stopColor="var(--color-premiumSpend)"
                  stopOpacity={0.1}
                />
              </linearGradient>
            </defs>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="date"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              minTickGap={32}
              tickFormatter={(value) => {
                const date = new Date(value)
                return date.toLocaleDateString('ru-RU', {
                  month: 'short',
                  day: 'numeric',
                })
              }}
            />

            <ChartTooltip
              cursor={false}
              content={
                <ChartTooltipContent
                  labelFormatter={(value) => {
                    return new Date(value).toLocaleDateString('ru-RU', {
                      month: 'short',
                      day: 'numeric',
                    })
                  }}
                  indicator="dot"
                />
              }
            />
            <Area
              dataKey="starsSpend"
              type="step"
              fill="url(#fillStarsSpend)"
              stroke="var(--color-starsSpend)"
            />
            <Area
              dataKey="premiumSpend"
              type="step"
              fill="url(#fillPremiumSpend)"
              stroke="var(--color-premiumSpend)"
            />
            <ChartLegend content={<ChartLegendContent />} />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}

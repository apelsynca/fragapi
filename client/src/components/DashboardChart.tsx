import { Area, AreaChart, CartesianGrid, XAxis } from 'recharts'

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '~/components/ui/card'
import type { ChartConfig } from '~/components/ui/chart'
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
} from '~/components/ui/chart'
import { useQuery } from '@tanstack/react-query'
import { fetchATransactionsChart } from '~/lib/different'

export const description = 'An interactive area chart'

const chartConfig = {
  visitors: {
    label: 'Статистика',
  },
  tonAmount: {
    label: 'TON',
    color: 'var(--chart-1)',
  },
  transactionsCount: {
    label: 'Покупок',
    color: 'var(--chart-2)',
  },
} satisfies ChartConfig

export default function DashboardChart() {
  const { data: chartData } = useQuery({
    queryKey: ['transactions', 'chart'],
    queryFn: () => fetchATransactionsChart(),
  })

  return (
    <Card className="pt-0">
      <CardHeader className="flex items-center gap-2 space-y-0 border-b py-5 sm:flex-row">
        <div className="grid flex-1 gap-1">
          <CardTitle>Статистика транзакций</CardTitle>
          <CardDescription>
            Показываем общие транзакции за последний месяц
          </CardDescription>
        </div>
      </CardHeader>
      <CardContent className="px-2 pt-4 sm:px-6 sm:pt-6">
        <ChartContainer
          config={chartConfig}
          className="aspect-auto h-62.5 w-full"
        >
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="fillTonAmount" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--color-tonAmount)"
                  stopOpacity={0.8}
                />
                <stop
                  offset="95%"
                  stopColor="var(--color-transactionsCount)"
                  stopOpacity={0.1}
                />
              </linearGradient>
              <linearGradient
                id="fillTransactionsCount"
                x1="0"
                y1="0"
                x2="0"
                y2="1"
              >
                <stop
                  offset="5%"
                  stopColor="var(--color-tonAmount)"
                  stopOpacity={0.8}
                />
                <stop
                  offset="95%"
                  stopColor="var(--color-transactionsCount)"
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
              dataKey="tonAmount"
              type="step"
              fill="url(#fillTonAmount)"
              stroke="var(--color-tonAmount)"
            />
            <Area
              dataKey="transactionsCount"
              type="step"
              fill="url(#fillTransactionsCount)"
              stroke="var(--color-transactionsCount)"
            />
            <ChartLegend content={<ChartLegendContent />} />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}

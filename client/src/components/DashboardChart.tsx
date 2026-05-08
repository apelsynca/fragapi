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

export const description = 'An interactive area chart'

const chartData = [
  { date: '2024-06-01', tonAmount: 178, transactionsCount: 200 },
  { date: '2024-06-02', tonAmount: 470, transactionsCount: 410 },
  { date: '2024-06-03', tonAmount: 103, transactionsCount: 160 },
  { date: '2024-06-04', tonAmount: 439, transactionsCount: 380 },
  { date: '2024-06-05', tonAmount: 88, transactionsCount: 140 },
  { date: '2024-06-06', tonAmount: 294, transactionsCount: 250 },
  { date: '2024-06-07', tonAmount: 323, transactionsCount: 370 },
  { date: '2024-06-08', tonAmount: 385, transactionsCount: 320 },
  { date: '2024-06-09', tonAmount: 438, transactionsCount: 480 },
  { date: '2024-06-10', tonAmount: 155, transactionsCount: 200 },
  { date: '2024-06-11', tonAmount: 92, transactionsCount: 150 },
  { date: '2024-06-12', tonAmount: 492, transactionsCount: 420 },
  { date: '2024-06-13', tonAmount: 81, transactionsCount: 130 },
  { date: '2024-06-14', tonAmount: 426, transactionsCount: 380 },
  { date: '2024-06-15', tonAmount: 307, transactionsCount: 350 },
  { date: '2024-06-16', tonAmount: 371, transactionsCount: 310 },
  { date: '2024-06-17', tonAmount: 475, transactionsCount: 520 },
  { date: '2024-06-18', tonAmount: 107, transactionsCount: 170 },
  { date: '2024-06-19', tonAmount: 341, transactionsCount: 290 },
  { date: '2024-06-20', tonAmount: 408, transactionsCount: 450 },
  { date: '2024-06-21', tonAmount: 169, transactionsCount: 210 },
  { date: '2024-06-22', tonAmount: 317, transactionsCount: 270 },
  { date: '2024-06-23', tonAmount: 480, transactionsCount: 530 },
  { date: '2024-06-24', tonAmount: 132, transactionsCount: 180 },
  { date: '2024-06-25', tonAmount: 141, transactionsCount: 190 },
  { date: '2024-06-26', tonAmount: 434, transactionsCount: 380 },
  { date: '2024-06-27', tonAmount: 448, transactionsCount: 490 },
  { date: '2024-06-28', tonAmount: 149, transactionsCount: 200 },
  { date: '2024-06-29', tonAmount: 103, transactionsCount: 160 },
  { date: '2024-06-30', tonAmount: 446, transactionsCount: 400 },
]

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
              <linearGradient id="fillDesktop" x1="0" y1="0" x2="0" y2="1">
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
              <linearGradient id="fillMobile" x1="0" y1="0" x2="0" y2="1">
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
              type="natural"
              fill="url(#fillMobile)"
              stroke="var(--color-tonAmount)"
              stackId="a"
            />
            <Area
              dataKey="transactionsCount"
              type="natural"
              fill="url(#fillDesktop)"
              stroke="var(--color-transactionsCount)"
              stackId="a"
            />
            <ChartLegend content={<ChartLegendContent />} />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}

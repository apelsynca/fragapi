import { Badge } from '#/components/ui/badge'
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '#/components/ui/card'
import { cn } from '#/lib/utils'
import { TrendingUpIcon } from 'lucide-react'

interface DashboardStatsCardProps {
  className?: string
  description: string
  amount: number
  fiatAmount: number
  percent?: number
}

export default function DashboardStatsCard({
  className,
  description,
  amount,
  fiatAmount,
  percent,
}: DashboardStatsCardProps) {
  return (
    <Card className={cn('w-full max-w-sm h-full', className)}>
      <CardHeader className="grid auto-rows-min grid-rows-[auto_auto] items-start gap-2 px-6 has-data-[slot=card-action]:grid-cols-[1fr_auto]">
        <CardDescription>{description}</CardDescription>
        <CardTitle className="flex flex-col text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
          {parseFloat(amount.toFixed(2))} TON
          <span className="text-sm text-muted-foreground">
            ~${parseFloat(fiatAmount.toFixed(2))}
          </span>
        </CardTitle>
        {percent !== undefined && (
          <CardAction className="col-start-2 row-span-2 row-start-1 self-start justify-self-end">
            <Badge
              variant="outline"
              className={`${percent > 0 ? 'text-green-400 border-green-400' : 'text-red-400 border-red-400'} text-xs gap-1`}
            >
              <TrendingUpIcon className="h-3 w-3" />
              {percent > 0 ? '+' : null}
              {percent}%
            </Badge>
          </CardAction>
        )}
      </CardHeader>
      <CardContent className="px-6">
        <CardDescription>За последние 30 дней</CardDescription>
      </CardContent>
    </Card>
  )
}

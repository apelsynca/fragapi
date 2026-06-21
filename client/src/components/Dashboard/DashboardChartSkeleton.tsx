import { Card, CardContent, CardHeader } from '../ui/card'
import { Skeleton } from '../ui/skeleton'

export default function DashboardChartSkeleton() {
  return (
    <Card className="pt-0">
      <CardHeader className="flex items-center gap-2 space-y-0 border-b py-5 sm:flex-row">
        <div className="grid flex-1 gap-1">
          <Skeleton className="w-44 h-5" />
          <Skeleton className="w-80 h-3 my-2.5" />
        </div>
      </CardHeader>
      <CardContent className="pt-6 sm:pt-8 aspect-auto h-62.5 w-full"></CardContent>
    </Card>
  )
}

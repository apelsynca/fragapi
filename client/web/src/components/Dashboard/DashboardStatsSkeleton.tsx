import { Card, CardContent, CardHeader } from '../ui/card'
import { Skeleton } from '../ui/skeleton'

const SkeletonCard = ({ withButton = false }: { withButton?: boolean }) => {
  return (
    <Card className="w-full max-w-sm h-full">
      <CardHeader className="grid auto-rows-min grid-rows-[auto_auto] items-start gap-2 px-6 has-data-[slot=card-action]:grid-cols-[1fr_auto]">
        <Skeleton className="w-16 h-4 mb-2" />
        <Skeleton className="w-24 h-6 mb-1" />
        <Skeleton className="w-12 h-3 mb-1" />
      </CardHeader>
      <CardContent className="px-6">
        {withButton ? (
          <Skeleton className="w-full h-7" />
        ) : (
          <Skeleton className="w-1/2 h-3" />
        )}
      </CardContent>
    </Card>
  )
}

export default function DashboardStatsSkeleton() {
  return (
    <div className="flex flex-col items-center md:grid md:grid-cols-4 gap-1.5 md:gap-2.5">
      <SkeletonCard withButton />
      <SkeletonCard />
      <SkeletonCard />
      <SkeletonCard />
    </div>
  )
}

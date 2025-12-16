import { Card, CardHeader } from "../ui/card";
import { Skeleton } from "../ui/skeleton";

const StatItemLoading = () => {
  return (
    <Card className="min-w-[150px] w-full">
      <CardHeader>
        <Skeleton className="h-3 w-20" />
        <Skeleton className="h-7 w-16 mt-1" />
      </CardHeader>
    </Card>
  );
};

export const StatsLoading = () => {
  return (
    <div className="flex gap-2 mt-2 flex-wrap md:flex-nowrap">
      <StatItemLoading />
      <StatItemLoading />
      <StatItemLoading />
    </div>
  );
};


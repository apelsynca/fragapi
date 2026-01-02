import { useSuspenseQuery } from "@tanstack/react-query";
import { transactionStatsQueryOptions } from "~/lib/options/transactions";
import { Card, CardDescription, CardHeader, CardTitle } from "../ui/card";

const StatItem: React.FC<{ title: string; value: string }> = ({
  title,
  value,
}) => {
  return (
    <Card className="min-w-[150px] w-full">
      <CardHeader>
        <CardDescription>{title}</CardDescription>
        <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
          {value}
        </CardTitle>
      </CardHeader>
    </Card>
  );
};

export const Stats = () => {
  const { data: stats } = useSuspenseQuery(transactionStatsQueryOptions());

  return (
    <div className="flex gap-2 mt-2 flex-wrap md:flex-nowrap">
      <StatItem
        title="Покупок звезд"
        value={`${stats.stars_purchases_count.toLocaleString()} раз`}
      />
      <StatItem
        title="Покупок premium"
        value={`${stats.premium_count.toLocaleString()} раз`}
      />
      <StatItem title="Потрачено" value={`${stats.total_spent.toLocaleString()} TON`} />
    </div>
  );
};

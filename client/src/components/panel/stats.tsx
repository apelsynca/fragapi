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
  return (
    <div className="flex gap-2 mt-2 flex-wrap md:flex-nowrap">
      <StatItem title="Купленно звезд" value="0" />
      <StatItem title="Купленно premium" value="0 раз." />
      <StatItem title="Потрачено" value="0 TON" />
      <StatItem title="Поисковых запросов" value="0" />
    </div>
  );
};

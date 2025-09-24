import { useQuery } from "@tanstack/react-query";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { Skeleton } from "../ui/skeleton";
import { meQueryOptions } from "~/lib/options/me";
import { TopUp } from "../layout/top-up";

export const Balance = () => {
  const { data: me, isLoading } = useQuery(meQueryOptions());

  if (isLoading || !me) {
    return (
      <div>
        <Card>
          <CardHeader>
            <CardDescription>
              <Skeleton className="h-4 w-[6ch]" />
            </CardDescription>
            <CardTitle>
              <Skeleton className="mt-2 h-7 w-[10ch]" />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Skeleton className="h-8 max-w-[8rem]" />
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div>
      <Card>
        <CardHeader>
          <CardDescription>Баланс</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
            {me.balance.toFixed(2)} TON
          </CardTitle>
        </CardHeader>
        <CardContent>
          <TopUp />
        </CardContent>
      </Card>
    </div>
  );
};

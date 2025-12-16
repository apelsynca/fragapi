import { createFileRoute } from "@tanstack/react-router";
import { Suspense } from "react";

import { Balance } from "~/components/panel/balance";
import { Stats } from "~/components/panel/stats";
import { StatsLoading } from "~/components/panel/stats-loading";
import { Transactions } from "~/components/transactions";
import { TransactionsLoading } from "~/components/transactions/loading";

export const Route = createFileRoute("/_panel/home")({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <div className="w-full max-w-[960px] mx-auto">
      <Balance />
      <Suspense fallback={<StatsLoading />}>
        <Stats />
      </Suspense>
      <Suspense fallback={<TransactionsLoading />}>
        <Transactions />
      </Suspense>
    </div>
  );
}

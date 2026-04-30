import { createServerFn } from "@tanstack/react-start";
import { queryOptions } from "@tanstack/react-query";
import { verifySession } from "./auth";
import { request } from "./client";
import type { Transaction, TransactionStats } from "./models/transactions";
import { type ListResource } from "./models/list";

export const fetchTransactions = createServerFn()
  .inputValidator((data: { page?: number; limit?: number }) => data)
  .handler(async ({ data }) => {
    const token = await verifySession();
    const params = new URLSearchParams();
    if (data.page) params.set("page", data.page.toString());
    if (data.limit) params.set("limit", data.limit.toString());

    const url = `/panel/transactions${params.toString() ? `?${params.toString()}` : ""}`;
    const response = await request(url, {
      token,
    });

    const json = await response.json();

    if (response.status !== 200) {
      console.log("Error fetching transactions", json);
      throw new Error("Error fetching transactions");
    }

    return json as ListResource<Transaction>;
  });

export const transactionsQueryOptions = (
  page: number = 1,
  limit: number = 10,
) =>
  queryOptions({
    queryKey: ["transactions", page, limit],
    queryFn: () => fetchTransactions({ data: { page, limit } }),
  });

export const fetchTransactionStats = createServerFn().handler(async () => {
  const token = await verifySession();
  const response = await request("/panel/transactions/stats", {
    token,
  });

  const json = await response.json();

  if (response.status !== 200) {
    console.log("Error fetching transaction stats", json);
    throw new Error("Error fetching transaction stats");
  }

  return json as TransactionStats;
});

export const transactionStatsQueryOptions = () =>
  queryOptions({
    queryKey: ["transactionStats"],
    queryFn: () => fetchTransactionStats(),
  });

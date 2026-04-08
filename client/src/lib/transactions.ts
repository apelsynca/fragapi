import { createServerFn } from "@tanstack/react-start";
import { verifySession } from "./auth";
import { request } from "./client";
import {
  Transaction,
  TransactionStats,
  TransactionVerifyResponse,
} from "./models/transactions";
import { ListResource } from "./models/list";

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

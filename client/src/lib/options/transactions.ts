import { queryOptions } from "@tanstack/react-query";
import { fetchTransactions, fetchTransactionStats } from "../transactions";

export const transactionsQueryOptions = (
  page: number = 1,
  limit: number = 10,
) =>
  queryOptions({
    queryKey: ["transactions", page, limit],
    queryFn: () => fetchTransactions({ data: { page, limit } }),
  });

export const transactionStatsQueryOptions = () =>
  queryOptions({
    queryKey: ["transactionStats"],
    queryFn: () => fetchTransactionStats(),
  });

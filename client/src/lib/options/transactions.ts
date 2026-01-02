import { queryOptions } from "@tanstack/react-query";
import { useServerFn } from "@tanstack/react-start";
import {
  fetchTransactions,
  fetchTransactionStats,
  verifyTransaction,
} from "../transactions";

export const transactionsQueryOptions = (
  page: number = 1,
  limit: number = 10,
) =>
  queryOptions({
    queryKey: ["transactions", page, limit],
    queryFn: () => useServerFn(fetchTransactions)({ data: { page, limit } }),
  });

export const transactionStatsQueryOptions = () =>
  queryOptions({
    queryKey: ["transactionStats"],
    queryFn: useServerFn(fetchTransactionStats),
  });

export const verifyTransactionFn = () => useServerFn(verifyTransaction);

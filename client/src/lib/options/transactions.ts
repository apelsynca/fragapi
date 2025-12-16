import { queryOptions } from "@tanstack/react-query";
import { useServerFn } from "@tanstack/react-start";
import { fetchTransactions, fetchTransactionStats } from "../transactions";

export const transactionsQueryOptions = () =>
  queryOptions({
    queryKey: ["transactions"],
    queryFn: useServerFn(fetchTransactions),
  });

export const transactionStatsQueryOptions = () =>
  queryOptions({
    queryKey: ["transactionStats"],
    queryFn: useServerFn(fetchTransactionStats),
  });

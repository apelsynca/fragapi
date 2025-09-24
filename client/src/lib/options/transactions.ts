import { queryOptions } from "@tanstack/react-query";
import { useServerFn } from "@tanstack/react-start";
import { fetchTransactions } from "../transactions";

export const transactionsQueryOptions = () =>
  queryOptions({
    queryKey: ["transactions"],
    queryFn: useServerFn(fetchTransactions),
  });

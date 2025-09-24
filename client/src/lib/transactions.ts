import { createServerFn } from "@tanstack/react-start";
import { verifySession } from "./auth";
import { request } from "./client";
import { Transaction } from "./models/transactions";
import { ListResource } from "./models/list";

export const fetchTransactions = createServerFn().handler(async () => {
  const token = await verifySession();
  const response = await request("/panel/transactions", {
    token,
  });

  const json = await response.json();

  if (response.status !== 200) {
    console.log("Error fetching transactions", json);
    throw new Error("Error fetching transactions");
  }

  return json as ListResource<Transaction>;
});

"use client";

import { ColumnDef } from "@tanstack/react-table";

import { Transaction, TransactionReason } from "~/lib/models/transactions";

const getFormattedReason = (reason: TransactionReason): string => {
  switch (reason) {
    case TransactionReason.STARS:
      return "Звезды";
    case TransactionReason.PREMIUM:
      return "Премиум";
    default:
      return reason;
  }
};

export const columns: ColumnDef<Transaction>[] = [
  {
    accessorKey: "amount",
    header: "Сумма",
    cell: ({ row }) => {
      const amount = parseFloat(row.getValue("amount"));
      const formatted = new Intl.NumberFormat("ru-RU", {
        style: "currency",
        currency: "TON",
      }).format(amount);

      return <div className="font-semibold">{formatted}</div>;
    },
  },
  {
    accessorKey: "reason",
    header: "Причина",
    cell: ({ row }) => {
      const reason: TransactionReason = row.getValue("reason");
      const formattedReason = getFormattedReason(reason);

      return <div>{formattedReason}</div>;
    },
  },
  {
    accessorKey: "created_at",
    header: () => <div className="text-right">Дата</div>,
    cell: ({ row }) => {
      const createdAt = Date.parse(row.getValue("created_at"));

      const formattedCreatedAt = new Intl.DateTimeFormat("ru-RU", {
        dateStyle: "short",
        timeStyle: "medium",
      }).format(createdAt);

      return <div className="text-right">{formattedCreatedAt}</div>;
    },
  },
];

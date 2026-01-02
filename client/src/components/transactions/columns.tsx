"use client";

import { ColumnDef } from "@tanstack/react-table";
import {
  CheckCircle,
  Clock,
  XCircle,
  ExternalLink,
  Star,
  Crown,
} from "lucide-react";

import {
  Transaction,
  TransactionReason,
  TransactionStatus,
} from "~/lib/models/transactions";
import { cn } from "~/lib/utils";

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

const getStatusIcon = (status: TransactionStatus) => {
  switch (status) {
    case TransactionStatus.COMPLETED:
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    case TransactionStatus.PENDING:
      return <Clock className="h-4 w-4 text-yellow-500" />;
    case TransactionStatus.FAILED:
      return <XCircle className="h-4 w-4 text-red-500" />;
    default:
      return null;
  }
};

const getStatusText = (status: TransactionStatus): string => {
  switch (status) {
    case TransactionStatus.COMPLETED:
      return "Выполнено";
    case TransactionStatus.PENDING:
      return "В обработке";
    case TransactionStatus.FAILED:
      return "Ошибка";
    default:
      return status;
  }
};

const getStatusClass = (status: TransactionStatus): string => {
  switch (status) {
    case TransactionStatus.COMPLETED:
      return "text-green-600 dark:text-green-400";
    case TransactionStatus.PENDING:
      return "text-yellow-600 dark:text-yellow-400";
    case TransactionStatus.FAILED:
      return "text-red-600 dark:text-red-400";
    default:
      return "";
  }
};

export const columns: ColumnDef<Transaction>[] = [
  {
    accessorKey: "status",
    header: "Статус",
    cell: ({ row }) => {
      const status: TransactionStatus = row.getValue("status");
      return (
        <div className={cn("flex items-center gap-1.5", getStatusClass(status))}>
          {getStatusIcon(status)}
          <span className="text-sm">{getStatusText(status)}</span>
        </div>
      );
    },
  },
  {
    accessorKey: "reason",
    header: "Тип",
    cell: ({ row }) => {
      const reason: TransactionReason = row.getValue("reason");
      const formattedReason = getFormattedReason(reason);
      const Icon = reason === TransactionReason.STARS ? Star : Crown;

      return (
        <div className="flex items-center gap-1.5">
          <Icon className="h-4 w-4 text-muted-foreground" />
          <span>{formattedReason}</span>
        </div>
      );
    },
  },
  {
    accessorKey: "recipient",
    header: "Получатель",
    cell: ({ row }) => {
      const recipient = row.original.recipient;
      return (
        <div className="text-sm">
          {recipient ? (
            <span className="font-medium">@{recipient}</span>
          ) : (
            <span className="text-muted-foreground">—</span>
          )}
        </div>
      );
    },
  },
  {
    accessorKey: "stars_quantity",
    header: "Кол-во",
    cell: ({ row }) => {
      const quantity = row.original.stars_quantity;
      const reason = row.original.reason;

      if (reason === TransactionReason.PREMIUM) {
        return <span className="text-muted-foreground">—</span>;
      }

      return (
        <div className="flex items-center gap-1">
          {quantity ? (
            <>
              <Star className="h-3.5 w-3.5 text-yellow-500 fill-yellow-500" />
              <span className="font-medium">{quantity.toLocaleString()}</span>
            </>
          ) : (
            <span className="text-muted-foreground">—</span>
          )}
        </div>
      );
    },
  },
  {
    accessorKey: "amount",
    header: "Сумма",
    cell: ({ row }) => {
      const amount = parseFloat(row.getValue("amount"));
      const formatted = new Intl.NumberFormat("ru-RU", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 4,
      }).format(amount);

      return <div className="font-semibold">{formatted} TON</div>;
    },
  },
  {
    accessorKey: "tx_hash",
    header: "Транзакция",
    cell: ({ row }) => {
      const txHash = row.original.tx_hash;

      if (!txHash) {
        return <span className="text-muted-foreground text-sm">—</span>;
      }

      const shortHash = `${txHash.slice(0, 6)}...${txHash.slice(-4)}`;
      const tonviewerUrl = `https://tonviewer.com/transaction/${txHash}`;

      return (
        <a
          href={tonviewerUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-sm text-blue-500 hover:text-blue-600 transition-colors"
        >
          <code className="font-mono">{shortHash}</code>
          <ExternalLink className="h-3 w-3" />
        </a>
      );
    },
  },
  {
    accessorKey: "created_at",
    header: () => <div className="text-right">Дата</div>,
    cell: ({ row }) => {
      const createdAt = Date.parse(row.getValue("created_at"));

      const formattedCreatedAt = new Intl.DateTimeFormat("ru-RU", {
        dateStyle: "short",
        timeStyle: "short",
      }).format(createdAt);

      return <div className="text-right text-sm">{formattedCreatedAt}</div>;
    },
  },
];

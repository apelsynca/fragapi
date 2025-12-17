"use client";

import { useState } from "react";
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import {
  useQuery,
  useQueryClient,
  useSuspenseQuery,
} from "@tanstack/react-query";
import {
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  RefreshCw,
  ShieldCheck,
} from "lucide-react";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";
import { Button } from "../ui/button";
import { columns } from "./columns";
import {
  transactionsQueryOptions,
  verifyTransactionFn,
} from "~/lib/options/transactions";
import { Transaction, TransactionStatus } from "~/lib/models/transactions";
import { toast } from "sonner";

const ITEMS_PER_PAGE = 10;

export const Transactions = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [verifyingId, setVerifyingId] = useState<number | null>(null);
  const queryClient = useQueryClient();

  const {
    data: { items: transactions, pagination },
  } = useSuspenseQuery(transactionsQueryOptions(currentPage, ITEMS_PER_PAGE));

  const verifyTx = verifyTransactionFn();

  const table = useReactTable({
    data: transactions,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  const handleVerify = async (transaction: Transaction) => {
    if (!transaction.tx_hash) {
      toast.error("У этой транзакции нет хеша для проверки");
      return;
    }

    setVerifyingId(transaction.id);
    try {
      const result = await verifyTx({ data: { transactionId: transaction.id } });

      if (result.verified) {
        toast.success(result.message);
      } else {
        toast.warning(result.message);
      }

      // Refresh transactions list
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
    } catch (error) {
      toast.error("Ошибка при проверке транзакции");
    } finally {
      setVerifyingId(null);
    }
  };

  const totalPages = pagination.max_page;
  const canGoPrevious = currentPage > 1;
  const canGoNext = currentPage < totalPages;

  return (
    <div className="mt-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">История транзакций</h3>
        <div className="text-sm text-muted-foreground">
          Всего: {pagination.total_count.toLocaleString()}
        </div>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext(),
                        )}
                  </TableHead>
                ))}
                <TableHead className="w-[80px]">Проверка</TableHead>
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </TableCell>
                  ))}
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleVerify(row.original)}
                      disabled={
                        verifyingId === row.original.id ||
                        !row.original.tx_hash
                      }
                      title={
                        row.original.tx_hash
                          ? "Проверить транзакцию в блокчейне"
                          : "Нет хеша для проверки"
                      }
                    >
                      {verifyingId === row.original.id ? (
                        <RefreshCw className="h-4 w-4 animate-spin" />
                      ) : (
                        <ShieldCheck
                          className={`h-4 w-4 ${
                            row.original.status === TransactionStatus.COMPLETED
                              ? "text-green-500"
                              : row.original.tx_hash
                                ? "text-muted-foreground"
                                : "text-muted-foreground/40"
                          }`}
                        />
                      )}
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length + 1}
                  className="h-24 text-center"
                >
                  Транзакций пока нет.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-2">
          <div className="text-sm text-muted-foreground">
            Страница {currentPage} из {totalPages}
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(1)}
              disabled={!canGoPrevious}
            >
              <ChevronsLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={!canGoPrevious}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>

            {/* Page numbers */}
            <div className="flex items-center gap-1">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                let pageNum: number;
                if (totalPages <= 5) {
                  pageNum = i + 1;
                } else if (currentPage <= 3) {
                  pageNum = i + 1;
                } else if (currentPage >= totalPages - 2) {
                  pageNum = totalPages - 4 + i;
                } else {
                  pageNum = currentPage - 2 + i;
                }

                return (
                  <Button
                    key={pageNum}
                    variant={currentPage === pageNum ? "default" : "outline"}
                    size="sm"
                    onClick={() => setCurrentPage(pageNum)}
                    className="w-8"
                  >
                    {pageNum}
                  </Button>
                );
              })}
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={!canGoNext}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(totalPages)}
              disabled={!canGoNext}
            >
              <ChevronsRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

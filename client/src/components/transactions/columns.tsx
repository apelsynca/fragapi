import { MoreHorizontalIcon } from 'lucide-react'
import type { ColumnDef } from '@tanstack/react-table'
import type { Transaction } from '~/server/models/transactions'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu'
import { Button } from '../ui/button'
import { TonIcon } from '../icons/TonIcon'

export const columns: ColumnDef<Transaction>[] = [
  {
    accessorKey: 'reason',
    header: 'Тип',
    cell: ({ row }) =>
      row.original.reason.toLowerCase() === 'stars' ? (
        <p className="text-yellow-800 dark:text-yellow-200">Звезды</p>
      ) : (
        <p className="text-blue-800 dark:text-blue-200">Премиум</p>
      ),
  },
  {
    accessorKey: 'createdAt',
    header: 'Дата создания',
    cell: ({ row }) => new Date(row.original.createdAt).toLocaleString(),
  },
  {
    accessorKey: 'recipient',
    header: 'Получатель',
    accessorFn: (transaction) =>
      `${transaction.recipient.slice(0, 8)}...${transaction.recipient.slice(-8, -1)}`,
  },
  {
    accessorKey: 'amount',
    header: 'Amount',
    cell: ({ row }) => (
      <span className="flex items-center gap-1">
        {parseFloat(row.original.amount.toFixed(2))} <TonIcon size={16} />
      </span>
    ),
  },
  {
    id: 'actions',
    cell: ({ row }) => {
      const transaction = row.original

      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost">
              <span className="sr-only">Открыть меню</span>
              <MoreHorizontalIcon className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>Действия</DropdownMenuLabel>
            <DropdownMenuItem
              onClick={() =>
                navigator.clipboard.writeText(transaction.message_hash!)
              }
            >
              Скопировать хэш
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() =>
                navigator.clipboard.writeText(transaction.recipient)
              }
            >
              Скопировать хэш получателя
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      )
    },
  },
]

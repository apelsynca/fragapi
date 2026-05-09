import type { ColumnDef } from '@tanstack/react-table'
import type { Transaction } from '~/lib/models/transactions'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu'
import { Button } from '../ui/button'
import { MoreHorizontalIcon } from 'lucide-react'

export const columns: ColumnDef<Transaction>[] = [
  {
    accessorKey: 'reason',
    header: 'Reason',
  },
  {
    accessorKey: 'recipient',
    header: 'Recipient',
    cell: ({ row }) => (
      <p>
        {row.original.recipient.slice(0, 8)}...
        {row.original.recipient.slice(-8, -1)}
      </p>
    ),
  },
  {
    accessorKey: 'amount',
    header: 'Amount',
  },
  {
    id: 'actions',
    cell: ({ row }) => {
      const transaction = row.original

      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost">
              <span className="sr-only">Open menu</span>
              <MoreHorizontalIcon className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>Actions</DropdownMenuLabel>
            <DropdownMenuItem
              onClick={() =>
                navigator.clipboard.writeText(transaction.message_hash!)
              }
            >
              Copy message hash
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem>View customer</DropdownMenuItem>
            <DropdownMenuItem>View payment details</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      )
    },
  },
]

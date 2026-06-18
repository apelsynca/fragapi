import type { ColumnDef } from '@tanstack/react-table'
import { CopyIcon, ExternalLinkIcon, MoreHorizontalIcon } from 'lucide-react'
import { toast } from 'sonner'
import { m } from '#/paraglide/messages'
import type { Payment } from '#/server-api/models/payments'
import { GramRoundedIcon } from '../icons/GramRoundedIcon'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu'
import { Button } from '../ui/button'

export const columns: ColumnDef<Payment>[] = [
  {
    header: m.amount(),
    cell: ({ row }) => (
      <span className="text-green-300 flex items-center gap-1.5 [&_svg]:size-3.5 font-medium">
        +{parseFloat(row.original.amount.toFixed(2))} GRAM <GramRoundedIcon />
      </span>
    ),
  },
  {
    header: m.created_at(),
    cell: ({ row }) => (
      <span>{new Date(row.original.createdAt).toLocaleString()}</span>
    ),
  },
  {
    id: 'actions',
    cell: ({ row }) => {
      const payment = row.original

      return (
        <DropdownMenu>
          <DropdownMenuTrigger>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <span className="sr-only">Open menu</span>
              <MoreHorizontalIcon className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuLabel>{m.actions()}</DropdownMenuLabel>
            {payment.transaction?.hash && (
              <>
                <DropdownMenuItem asChild>
                  <a
                    href={`https://tonscan.org/tx/${payment.transaction.hash}`}
                    target="_blank"
                    rel="noreferrer noopener"
                  >
                    <ExternalLinkIcon /> Scan
                  </a>
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => {
                    navigator.clipboard.writeText(payment.transaction!.hash!)
                    toast.success(m.copied_transaction_hash())
                  }}
                >
                  <CopyIcon /> {m.copy_hash()}
                </DropdownMenuItem>
              </>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      )
    },
  },
]

import type { ColumnDef } from '@tanstack/react-table'
import {
  CopyIcon,
  ExternalLinkIcon,
  MoonIcon,
  MoreHorizontalIcon,
  StarIcon,
} from 'lucide-react'
import type { FragmentTransaction } from '#/server-api/models/transactions'
import { GramRoundedIcon } from '../icons/GramRoundedIcon'
import { m } from '#/paraglide/messages'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu'
import { Button } from '../ui/button'
import { toast } from 'sonner'

const ActionsCompik = ({ payment }: { payment: FragmentTransaction }) => (
  <DropdownMenu>
    <DropdownMenuTrigger asChild>
      <Button variant="ghost" className="h-8 w-8 p-0">
        <span className="sr-only">Open menu</span>
        <MoreHorizontalIcon className="h-4 w-4" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent>
      <DropdownMenuLabel>{m.actions()}</DropdownMenuLabel>
      {payment.tonTransaction.hash && (
        <>
          <DropdownMenuItem asChild>
            <a
              href={`https://tonscan.org/tx/${payment.tonTransaction.hash}`}
              target="_blank"
              rel="noreferrer noopener"
            >
              <ExternalLinkIcon /> Scan
            </a>
          </DropdownMenuItem>
          <DropdownMenuItem
            onClick={() => {
              navigator.clipboard.writeText(payment.tonTransaction.hash!)
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

export const columns: ColumnDef<FragmentTransaction>[] = [
  {
    header: m.amount(),
    cell: ({ row }) => (
      <span className="flex items-center gap-1.5 [&_svg]:size-3.5 font-medium">
        {parseFloat(row.original.amount.toFixed(2))} <GramRoundedIcon />
      </span>
    ),
  },
  {
    header: m.reason(),
    cell: ({ row }) => {
      const reason = row.original.reason
      if (reason === 'stars') {
        return (
          <span className="text-yellow-600 dark:text-yellow-300 font-medium">
            Stars
          </span>
        )
      }
      return (
        <span className="text-purple-600 dark:text-purple-300 font-medium">
          Premium
        </span>
      )
    },
  },
  {
    header: m.username(),
    cell: ({ row }) => `@${row.original.recipientUsername}`,
  },
  {
    header: 'Payload',
    cell: ({ row }) => (
      <span className="font-semibold flex items-center gap-0.5">
        {row.original.premiumMonths ? (
          <>
            {row.original.premiumMonths} <MoonIcon className="w-4 h-4" />
          </>
        ) : (
          <>
            {row.original.starsAmount} <StarIcon className="w-4 h-4" />
          </>
        )}
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
      return <ActionsCompik payment={payment} />
    },
  },
]

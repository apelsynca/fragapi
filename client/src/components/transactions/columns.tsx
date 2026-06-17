import type { ColumnDef } from '@tanstack/react-table'
import { MoonIcon, StarIcon } from 'lucide-react'
import type { FragmentTransaction } from '#/server-api/models/transactions'
import { GramRoundedIcon } from '../icons/GramRoundedIcon'
import { m } from '#/paraglide/messages'

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
    accessorKey: 'reason',
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
    accessorKey: 'recipientUsername',
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
    accessorKey: 'createdAt',
    header: m.created_at(),
    cell: ({ row }) => (
      <span>{new Date(row.original.createdAt).toLocaleString()}</span>
    ),
  },
]

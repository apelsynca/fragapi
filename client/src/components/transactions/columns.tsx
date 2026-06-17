import type { ColumnDef } from '@tanstack/react-table'
import { MoonIcon, StarIcon } from 'lucide-react'
import type { FragmentTransaction } from '#/notserver/models/transactions'
import { GramRoundedIcon } from '../icons/GramRoundedIcon'

export const columns: ColumnDef<FragmentTransaction>[] = [
  {
    header: 'Amount',
    cell: ({ row }) => (
      <span className="flex items-center gap-1.5 [&_svg]:size-4 font-medium">
        {parseFloat(row.original.amount.toFixed(2))}{' '}
        <GramRoundedIcon size={22} />
      </span>
    ),
  },
  {
    accessorKey: 'reason',
    header: 'Reason',
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
    header: 'Username',
    cell: ({ row }) => `@${row.original.recipientUsername}`,
  },
  {
    header: 'Value',
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
    header: 'Date',
    cell: ({ row }) => (
      <span>{new Date(row.original.createdAt).toLocaleString()}</span>
    ),
  },
]

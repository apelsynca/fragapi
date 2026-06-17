import type { ColumnDef } from '@tanstack/react-table'
import { GramRoundedIcon } from '../icons/GramRoundedIcon'
import type { Payment } from '#/server-api/models/payments'
import { m } from '#/paraglide/messages'

export const columns: ColumnDef<Payment>[] = [
  {
    header: m.amount(),
    cell: ({ row }) => (
      <span className="flex items-center gap-1.5 [&_svg]:size-3.5 font-medium">
        {parseFloat(row.original.amount.toFixed(2))} <GramRoundedIcon />
      </span>
    ),
  },
  {
    header: m.created_at(),
    cell: ({ row }) => (
      <span>{new Date(row.original.createdAt).toLocaleString()}</span>
    ),
  },
]

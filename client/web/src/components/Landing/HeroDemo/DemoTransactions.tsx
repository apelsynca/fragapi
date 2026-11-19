import { MoonIcon, StarIcon } from 'lucide-react'
import { isNewRow, rowTime } from './demoState'
import type { DemoRow } from './demoState'
import { GramRoundedIcon } from '#/components/icons/GramRoundedIcon'
import { Card } from '#/components/ui/card'
import { cn } from '#/lib/utils'
import { m } from '#/paraglide/messages'

/** Mirrors the columns of the real transactions table. */
export default function DemoTransactions({ rows }: { rows: DemoRow[] }) {
  return (
    <Card aria-hidden className="shrink-0 gap-0 py-0">
      <p className="border-b px-4 py-3 text-base leading-snug font-medium">
        {m.transactions()}
      </p>
      <table className="w-full">
        <thead>
          <tr className="text-muted-foreground border-b text-left [&>th]:h-9 [&>th]:px-4 [&>th]:font-medium">
            <th>{m.amount()}</th>
            <th>{m.reason()}</th>
            <th>{m.username()}</th>
            <th className="hidden sm:table-cell">Payload</th>
            <th className="hidden text-right sm:table-cell">
              {m.created_at()}
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const { purchase } = row
            const isStars = purchase.kind === 'stars'

            return (
              <tr
                key={row.id}
                className={cn(
                  'border-b last:border-0 [&>td]:h-10 [&>td]:px-4',
                  isNewRow(row) &&
                    'animate-in fade-in slide-in-from-top-2 duration-500',
                )}
              >
                <td>
                  <span className="flex items-center gap-1.5 font-medium tabular-nums">
                    {purchase.amount} <GramRoundedIcon size={14} />
                  </span>
                </td>
                <td
                  className={cn(
                    'font-medium',
                    isStars
                      ? 'text-yellow-600 dark:text-yellow-300'
                      : 'text-purple-600 dark:text-purple-300',
                  )}
                >
                  {isStars ? 'Stars' : 'Premium'}
                </td>
                <td>@{purchase.username}</td>
                <td className="hidden sm:table-cell">
                  <span className="flex items-center gap-0.5 font-semibold tabular-nums">
                    {purchase.quantity}
                    {isStars ? (
                      <StarIcon className="size-4" />
                    ) : (
                      <MoonIcon className="size-4" />
                    )}
                  </span>
                </td>
                <td className="text-muted-foreground hidden text-right tabular-nums sm:table-cell">
                  {rowTime(row.id)}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </Card>
  )
}

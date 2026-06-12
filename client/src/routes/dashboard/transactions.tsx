import { Suspense } from 'react'
import { createFileRoute } from '@tanstack/react-router'
import TransactionsList from '~/components/transactions/TransactionsList'

export const Route = createFileRoute('/dashboard/transactions')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div>
      <div className="mb-6 text-center">
        <h2 className="text-center font-semibold text-xl">
          {m('transactions')}
        </h2>
        <p className="text-muted-foreground text-sm">
          {m('transactions_desc')}
        </p>
      </div>
      <Suspense>
        <TransactionsList />
      </Suspense>
    </div>
  )
}

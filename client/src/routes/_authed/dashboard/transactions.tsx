import { createFileRoute } from '@tanstack/react-router'
import { Suspense } from 'react'
import TransactionsList from '~/components/transactions/TransactionsList'

export const Route = createFileRoute('/_authed/dashboard/transactions')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div>
      <div className="mb-6 text-center">
        <h2 className="text-center font-semibold text-xl">Транзакции</h2>
        <p className="text-muted-foreground text-sm">
          История ваших транзакций
        </p>
      </div>
      <Suspense>
        <TransactionsList />
      </Suspense>
    </div>
  )
}

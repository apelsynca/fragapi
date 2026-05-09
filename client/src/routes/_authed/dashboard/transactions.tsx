import { createFileRoute } from '@tanstack/react-router'
import { Suspense } from 'react'
import TransactionsList from '~/components/transactions/TransactionsList'

export const Route = createFileRoute('/_authed/dashboard/transactions')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div>
      <h2 className="text-center">Транзакции</h2>
      <Suspense>
        <TransactionsList />
      </Suspense>
    </div>
  )
}

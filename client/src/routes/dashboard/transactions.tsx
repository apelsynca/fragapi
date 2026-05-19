import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/dashboard/transactions')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Transactions</div>
}

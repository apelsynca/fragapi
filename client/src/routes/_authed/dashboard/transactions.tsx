import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_authed/dashboard/transactions')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div>
      <h2 className="text-center">Транзакции</h2>
    </div>
  )
}

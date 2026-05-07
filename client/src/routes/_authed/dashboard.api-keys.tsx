import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_authed/dashboard/api-keys')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Тут апи ключи</div>
}

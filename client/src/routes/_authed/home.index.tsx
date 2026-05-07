import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_authed/home/')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/_authed/home/"!</div>
}

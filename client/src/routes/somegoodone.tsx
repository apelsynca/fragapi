import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/somegoodone')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Somegoodone</div>
}

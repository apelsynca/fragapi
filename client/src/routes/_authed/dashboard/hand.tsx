import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_authed/dashboard/hand')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>ABCDEF</div>
}

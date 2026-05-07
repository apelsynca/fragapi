import { createFileRoute, Outlet } from '@tanstack/react-router'

export const Route = createFileRoute('/_authed/home')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div className="abc">
      <Outlet />
    </div>
  )
}

import { createFileRoute, Outlet } from '@tanstack/react-router'

export const Route = createFileRoute('/_authed/dashboard')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div className="abc">
      <div>This is layout of dashboard text</div>
      <Outlet />
    </div>
  )
}

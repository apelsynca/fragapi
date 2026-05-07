import { createFileRoute, Outlet } from '@tanstack/react-router'
import { useServerFn } from '@tanstack/react-start'
import { Button } from '#/components/ui/button'
import { logoutFn } from '#/lib/auth'

export const Route = createFileRoute('/_authed/dashboard')({
  component: RouteComponent,
})

function RouteComponent() {
  const logout = useServerFn(logoutFn)

  return (
    <div className="abc">
      <div>
        This is layout of dashboard text
        <Button
          variant="destructive"
          onClick={async () => {
            await logout()
          }}
        >
          Logout
        </Button>
      </div>
      <Outlet />
    </div>
  )
}

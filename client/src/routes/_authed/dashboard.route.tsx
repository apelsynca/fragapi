import { createFileRoute, Outlet } from '@tanstack/react-router'
import { TooltipProvider } from '#/components/ui/tooltip'
import AppSidebar from '#/components/AppSidebar'
import { SidebarProvider, SidebarTrigger } from '#/components/ui/sidebar'

export const Route = createFileRoute('/_authed/dashboard')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <TooltipProvider>
      <SidebarProvider>
        <AppSidebar />
        <div className="abc">
          <SidebarTrigger />
          <Outlet />
        </div>
      </SidebarProvider>
    </TooltipProvider>
  )
}

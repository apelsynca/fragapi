import { Toaster } from 'sonner'
import { TonConnectUIProvider } from '@tonconnect/ui-react'
import { createFileRoute, Outlet } from '@tanstack/react-router'
import { TooltipProvider } from '#/components/ui/tooltip'
import AppSidebar from '#/components/AppSidebar'
import { SidebarProvider, SidebarTrigger } from '#/components/ui/sidebar'
import { userMeQueryOptions } from '#/lib/user'

export const Route = createFileRoute('/_authed/dashboard')({
  component: RouteComponent,
  loader: async ({ context }) => {
    await context.queryClient.ensureQueryData(userMeQueryOptions())
  },
})

// idk about p-4 globally
function RouteComponent() {
  return (
    <TonConnectUIProvider manifestUrl={import.meta.env.VITE_MANIFEST_URL}>
      <TooltipProvider>
        <SidebarProvider>
          <AppSidebar />
          <main className="w-full relative">
            <SidebarTrigger className="ml-2 mt-2 absolute" />
            <div className="mt-8 pt-4 px-2 md:px-4 w-full max-w-7xl mx-auto">
              <Outlet />
            </div>
            <Toaster theme="system" richColors />
          </main>
        </SidebarProvider>
      </TooltipProvider>
    </TonConnectUIProvider>
  )
}

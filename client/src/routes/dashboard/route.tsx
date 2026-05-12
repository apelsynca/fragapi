import { Toaster } from 'sonner'
import { createFileRoute, Outlet } from '@tanstack/react-router'
import { SidebarProvider, SidebarTrigger } from '~/components/ui/sidebar'
import { TooltipProvider } from '~/components/ui/tooltip'
import AppSidebar from '~/components/AppSidebar'
import Providers from '~/components/Providers'
import Landing from '~/components/Landing'

export const Route = createFileRoute('/dashboard')({
  beforeLoad: ({ context }) => {
    if (!context.token) {
      throw new Error('Not authenticated')
    }
  },
  errorComponent: ({ error }) => {
    if (error.message === 'Not authenticated') {
      return <Landing />
    }

    throw error
  },
  component: DashboardComponent,
})

function DashboardComponent() {
  return (
    <TooltipProvider>
      <SidebarProvider>
        <Providers>
          <AppSidebar />
          <main className="w-full relative">
            <SidebarTrigger className="ml-2 mt-2 absolute" />
            <div className="mt-8 pt-4 px-2 md:px-4 w-full max-w-7xl mx-auto">
              <Outlet />
            </div>
            <Toaster theme="system" richColors />
          </main>
        </Providers>
      </SidebarProvider>
    </TooltipProvider>
  )
}

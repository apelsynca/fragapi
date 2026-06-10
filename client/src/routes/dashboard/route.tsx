import { Toaster } from 'sonner'
import { createFileRoute, Outlet } from '@tanstack/react-router'
import { SidebarProvider, SidebarTrigger } from '~/components/ui/sidebar'
import { userMeOptions } from '~/lib/queries'
import { TooltipProvider } from '~/components/ui/tooltip'
import DashboardProviders from '~/components/Dashboard/DashboardProviders'
import Landing from '~/components/Landing'
import AppSidebar from '~/components/AppSidebar'

export const Route = createFileRoute('/dashboard')({
  beforeLoad: ({ context }) => {
    if (!context.token) {
      throw new Error('Not authenticated')
    }
  },
  loader: ({ context }) => {
    context.queryClient.fetchQuery(userMeOptions())
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
        <DashboardProviders>
          <AppSidebar />
          <main className="w-full relative">
            <SidebarTrigger className="ml-2 mt-2 absolute" />
            <div className="mt-8 pt-4 px-2 md:px-4 w-full max-w-7xl mx-auto">
              <Outlet />
            </div>
            <Toaster theme="system" richColors />
          </main>
        </DashboardProviders>
      </SidebarProvider>
    </TooltipProvider>
  )
}

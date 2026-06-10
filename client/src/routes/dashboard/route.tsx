import { Toaster } from 'sonner'
import { useTranslation } from 'react-i18next'
import { createFileRoute, Outlet } from '@tanstack/react-router'
import { SidebarProvider, SidebarTrigger } from '~/components/ui/sidebar'
import { userMeOptions } from '~/lib/queries'
import { TooltipProvider } from '~/components/ui/tooltip'
import DashboardProviders from '~/components/Dashboard/DashboardProviders'
import Landing from '~/components/Landing'
import AppSidebar from '~/components/AppSidebar'
import { Separator } from '~/components/ui/separator'

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
  const { t } = useTranslation()

  return (
    <TooltipProvider>
      <SidebarProvider>
        <DashboardProviders>
          <AppSidebar />
          <main className="w-full relative">
            <div className="flex items-center gap-2 absolute mx-1 my-1">
              <SidebarTrigger className="px-2 py-2" />
              <Separator orientation="vertical" />
              <h2 className="text-base font-medium">{t('dashboard')}</h2>
            </div>
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

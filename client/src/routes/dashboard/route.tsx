import { Toaster } from 'sonner'
import { createFileRoute, Outlet, redirect } from '@tanstack/react-router'
import DashboardProviders from '~/layout/DashboardProviders'
import AppSidebar from '~/components/AppSidebar'
import DashboardTopBar from '~/components/Dashboard/DashboardTopBar'

export const Route = createFileRoute('/dashboard')({
  beforeLoad: ({ context }) => {
    if (!context.token) {
      throw new Error('Not authenticated')
    }
  },
  errorComponent: ({ error }) => {
    if (error.message === 'Not authenticated') {
      throw redirect({ to: '/' })
    }

    throw error
  },
  component: DashboardComponent,
})

function DashboardComponent() {
  return (
    <DashboardProviders>
      <AppSidebar />
      <main className="w-full bg-sidebar min-h-screen">
        <div className="md:rounded-xl md:m-2 bg-background">
          <DashboardTopBar />
          <div className="pt-4 pb-6 px-2 md:px-4 w-full h-full max-w-7xl mx-auto">
            <Outlet />
          </div>
          <Toaster theme="system" richColors />
        </div>
      </main>
    </DashboardProviders>
  )
}

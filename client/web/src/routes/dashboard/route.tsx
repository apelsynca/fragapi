import { Toaster } from 'sonner'
import {
  createFileRoute,
  isRedirect,
  Outlet,
  redirect,
} from '@tanstack/react-router'
import DashboardProviders from '#/layout/DashboardProviders'
import AppSidebar from '#/components/AppSidebar'
import DashboardTopBar from '#/components/Dashboard/DashboardTopBar'
import { m } from '#/paraglide/messages'

export const Route = createFileRoute('/dashboard')({
  beforeLoad: ({ context }) => {
    if (!context.token) {
      throw redirect({ to: '/' })
    }
  },
  errorComponent: ({ error }) => {
    if (isRedirect(error)) {
      return <SessionExpired />
    }

    throw error
  },
  component: DashboardComponent,
})

function SessionExpired() {
  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <div className="text-center space-y-2">
        <h2 className="text-lg font-semibold">{m.session_expired_title()}</h2>
        <p className="text-muted-foreground text-sm">
          {m.session_expired_desc()}
        </p>
      </div>
    </div>
  )
}

function DashboardComponent() {
  return (
    <DashboardProviders>
      <AppSidebar />
      <main className="w-full bg-sidebar min-h-screen md:p-2">
        <div className="md:rounded-xl bg-background h-full">
          <DashboardTopBar />
          <div className="pt-4 pb-6 px-2 md:px-4 w-full max-w-7xl mx-auto">
            <Outlet />
          </div>
          <Toaster theme="system" richColors />
        </div>
      </main>
    </DashboardProviders>
  )
}

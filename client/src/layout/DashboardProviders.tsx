import { TonConnectUIProvider } from '@tonconnect/ui-react'
import { SidebarProvider } from '#/components/ui/sidebar'
import { TooltipProvider } from '#/components/ui/tooltip'
import { ThemeProvider } from '#/components/theme-provider'

export default function DashboardProviders({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ThemeProvider defaultTheme="system" storageKey="theme">
      <TooltipProvider>
        <SidebarProvider>
          <TonConnectUIProvider
            manifestUrl={import.meta.env.VITE_MANIFEST_URL}
            analytics={{ mode: 'off' }}
          >
            {children}
          </TonConnectUIProvider>
        </SidebarProvider>
      </TooltipProvider>
    </ThemeProvider>
  )
}

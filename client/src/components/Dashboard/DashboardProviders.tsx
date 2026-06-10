import { TonConnectUIProvider } from '@tonconnect/ui-react'

export default function DashboardProviders({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <TonConnectUIProvider manifestUrl={import.meta.env.VITE_MANIFEST_URL}>
      {children}
    </TonConnectUIProvider>
  )
}

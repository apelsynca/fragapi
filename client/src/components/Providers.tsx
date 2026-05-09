import { TonConnectUIProvider } from '@tonconnect/ui-react'

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <TonConnectUIProvider manifestUrl={import.meta.env.VITE_MANIFEST_URL}>
      {children}
    </TonConnectUIProvider>
  )
}

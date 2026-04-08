import { createFileRoute, Outlet } from "@tanstack/react-router";
import { TonConnectUIProvider } from "@tonconnect/ui-react";

import { AppSidebar } from "~/components/layout/app-sidebar";
import { SidebarProvider, SidebarTrigger } from "~/components/ui/sidebar";
import { Toaster } from "~/components/ui/sonner";

export const Route = createFileRoute("/_panel")({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <TonConnectUIProvider manifestUrl="https://panel.fragapi.ru/tonconnect-manifest.json">
      <SidebarProvider>
        <AppSidebar />
        <main className="p-4 w-full max-w-screen">
          <SidebarTrigger className="mb-2" />
          <Outlet />
        </main>
        <Toaster position="top-center" />
      </SidebarProvider>
    </TonConnectUIProvider>
  );
}

import { useQuery } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "~/components/ui/sidebar";
import { meQueryOptions } from "~/lib/options/me";
import { Skeleton } from "../ui/skeleton";
import { TonWallet } from "./ton-wallet";

export const AppSidebar: React.FC = () => {
  const { data: me } = useQuery(meQueryOptions());
  const { setOpenMobile } = useSidebar();

  const closeSidebarMobile = () => {
    setOpenMobile(false);
  };

  return (
    <Sidebar>
      <SidebarHeader>
        <SidebarGroup>
          <SidebarMenu>
            <SidebarMenuItem onClick={closeSidebarMobile}>
              <Link to="/home" className="flex gap-2">
                <img src="/logo-dark.svg" alt="logo" />
                <h3 className="text-xl font-bold">Fragment API</h3>
              </Link>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroup>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem onClick={closeSidebarMobile}>
                <SidebarMenuButton asChild>
                  <Link to="/home">Главная</Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
        <SidebarGroup>
          <SidebarGroupLabel>TON API</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem onClick={closeSidebarMobile}>
                <SidebarMenuButton asChild>
                  <Link to="/tonapi/api-keys">API Ключи</Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <SidebarGroup>
          <SidebarGroupContent>
            {me ? (
              <span className="text-md font-semibold">
                {me.firstName} {me.lastName}
              </span>
            ) : (
              <Skeleton className="h-3 w-[12ch]" />
            )}
          </SidebarGroupContent>
        </SidebarGroup>
        <SidebarGroup>
          <SidebarGroupContent>
            <TonWallet />
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarFooter>
    </Sidebar>
  );
};

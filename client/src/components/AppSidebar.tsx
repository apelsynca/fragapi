import { Link } from '@tanstack/react-router'
import {
  ExternalLinkIcon,
  HomeIcon,
  JoystickIcon,
  KeySquareIcon,
  ListIcon,
} from 'lucide-react'
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
} from './ui/sidebar'
import AppSidebarBottom from './AppSidebarBottom'
import { Suspense } from 'react'
import AppSidebarBottomSkeleton from './AppSidebarBottomSkeleton'

function AppSidebar() {
  return (
    <Sidebar>
      <SidebarHeader />
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link to="/dashboard">
                    <HomeIcon /> Главная
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link to="/dashboard/transactions">
                    <ListIcon /> Транзакции
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link to="/dashboard/api-keys">
                    <KeySquareIcon /> API Ключи
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>

          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuButton asChild>
                <a href="https://docs.fragapi.com">
                  <ExternalLinkIcon /> Документация
                </a>
              </SidebarMenuButton>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>Другое</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenuItem>
              <SidebarMenuButton asChild>
                <Link to="/dashboard/hand">
                  <JoystickIcon /> Ручная отправка
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <Suspense fallback={<AppSidebarBottomSkeleton />}>
              <AppSidebarBottom />
            </Suspense>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar

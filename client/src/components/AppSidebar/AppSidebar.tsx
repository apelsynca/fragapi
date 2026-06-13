import { Link } from '@tanstack/react-router'
import {
  ExternalLinkIcon,
  HomeIcon,
  KeySquareIcon,
  ListIcon,
} from 'lucide-react'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarSeparator,
} from '~/components/ui/sidebar'
import { Suspense } from 'react'
import AppSidebarBottom from './AppSidebarBottom'
import { m } from '~/paraglide/messages'

function AppSidebarBottomSkeleton() {
  return <div>Bottom loading...</div>
}

function AppSidebar() {
  return (
    <Sidebar variant="inset">
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link to="/dashboard">
                    <HomeIcon /> {m.sidebar_main()}
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link to="/dashboard/transactions">
                    <ListIcon /> {m.sidebar_transactions()}
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link to="/dashboard/api-tokens">
                    <KeySquareIcon /> {m.sidebar_api_tokens()}
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarSeparator />

        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuButton asChild>
                <a href="https://docs.fragapi.com">
                  <ExternalLinkIcon /> {m.sidebar_docs()}
                </a>
              </SidebarMenuButton>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <SidebarMenu>
          <Suspense fallback={<AppSidebarBottomSkeleton />}>
            <AppSidebarBottom />
          </Suspense>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar

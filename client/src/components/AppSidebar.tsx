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
import { useTranslation } from 'react-i18next'

function AppSidebar() {
  const { t } = useTranslation()

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
                    <HomeIcon /> {t('sidebar.main')}
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton>
                  <ListIcon /> {t('sidebar.transactions')}
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link to="/dashboard/api-keys">
                    <KeySquareIcon /> {t('sidebar.api_keys')}
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>

          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuButton asChild>
                <a href="https://docs.fragapi.com">
                  <ExternalLinkIcon /> {t('sidebar.docs')}
                </a>
              </SidebarMenuButton>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>{t('sidebar.other')}</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenuItem>
              <SidebarMenuButton>
                <JoystickIcon /> {t('sidebar.hand_send')}
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

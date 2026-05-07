import { useServerFn } from '@tanstack/react-start'
import { logoutFn } from '#/lib/auth'
import { Button } from './ui/button'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from './ui/sidebar'
import { Link, useLocation } from '@tanstack/react-router'
import { HomeIcon, KeySquareIcon } from 'lucide-react'

function AppSidebar() {
  const logout = useServerFn(logoutFn)
  const location = useLocation()

  return (
    <Sidebar>
      <SidebarHeader />
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton
                  asChild
                  isActive={location.pathname == '/dashboard'}
                >
                  <Link to="/dashboard">
                    <HomeIcon /> Главная
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>

          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton
                  asChild
                  isActive={location.pathname == '/dashboard/api-keys'}
                >
                  <Link to="/dashboard/api-keys">
                    <KeySquareIcon /> API Ключи
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <Button
          variant="destructive"
          onClick={async () => {
            await logout()
          }}
        >
          Выйти
        </Button>
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar

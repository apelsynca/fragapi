import { HomeIcon, JoystickIcon, KeySquareIcon } from 'lucide-react'
import { useServerFn } from '@tanstack/react-start'
import { logoutFn } from '#/lib/auth'
import { Button } from './ui/button'
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
import { Link } from '@tanstack/react-router'
import ThemeToggle from './ThemeToggle'

function AppSidebar() {
  const logout = useServerFn(logoutFn)

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
            </SidebarMenu>
          </SidebarGroupContent>

          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link to="/dashboard/api-keys">
                    <KeySquareIcon /> API Ключи
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
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
        <div className="flex gap-1">
          <Button
            className="flex-1"
            variant="destructive"
            onClick={async () => {
              await logout()
            }}
          >
            Выйти
          </Button>
          <ThemeToggle />
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar

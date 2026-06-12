import { useServerFn } from '@tanstack/react-start'
import { useQueryClient, useSuspenseQuery } from '@tanstack/react-query'
import { useTonConnectUI, useTonWallet } from '@tonconnect/ui-react'
import {
  ChevronsUpDownIcon,
  LogOutIcon,
  PlugZapIcon,
  UnplugIcon,
} from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu'
import { Avatar, AvatarFallback, AvatarImage } from '~/components/ui/avatar'
import { SidebarMenuButton, useSidebar } from '~/components/ui/sidebar'
import { logoutFn } from '~/notserver/auth-manager'
import DashboardThemeToggle from './AppSidebarThemeToggle'
import { userMeOptions } from '~/lib/queries'

const LanguageToggle = () => {
  return <div>I am language toggle</div>
}

export default function AppSidebarBottom() {
  const logout = useServerFn(logoutFn)
  const queryClient = useQueryClient()
  const { data: user } = useSuspenseQuery(userMeOptions())

  const { isMobile } = useSidebar()

  const wallet = useTonWallet()
  const [tonConnectUI] = useTonConnectUI()

  const handleLogout = async () => {
    queryClient.invalidateQueries()
    await logout()
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <SidebarMenuButton size="lg">
          <div className="font-semibold">
            {user.firstName} {user.lastName}
          </div>
          <ChevronsUpDownIcon className="ml-auto size-4" />{' '}
        </SidebarMenuButton>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        className="w-(--radix-dropdown-menu-trigger-width) min-w-48 rounded-lg"
        side={isMobile ? 'bottom' : 'right'}
        align="end"
        sideOffset={4}
      >
        <DropdownMenuGroup>
          <DropdownMenuLabel className="p-0 font-normal">
            <div className="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
              <Avatar>
                <AvatarImage src={undefined} alt={user.firstName} />
                <AvatarFallback>
                  {user.firstName.slice(0, 2).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-medium">{user.firstName}</span>
                {user.username && (
                  <span className="truncate text-xs">@{user.username}</span>
                )}
              </div>
            </div>
          </DropdownMenuLabel>
          <DashboardThemeToggle />
          {wallet === null ? (
            <DropdownMenuItem onClick={() => tonConnectUI.openModal()}>
              <PlugZapIcon /> {'connect_wallet'}
            </DropdownMenuItem>
          ) : (
            <DropdownMenuItem onClick={() => tonConnectUI.disconnect()}>
              <UnplugIcon /> {'disconnect_wallet'}
            </DropdownMenuItem>
          )}
          <LanguageToggle />
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuGroup className="flex gap-1">
          <DropdownMenuItem
            className="flex-1 w-full"
            variant="destructive"
            onClick={handleLogout}
          >
            <LogOutIcon />
            {'sidebar.logout'}
          </DropdownMenuItem>
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

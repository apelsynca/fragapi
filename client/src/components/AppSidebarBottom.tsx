import { useTonConnectUI, useTonWallet } from '@tonconnect/ui-react'
import { useSuspenseQuery } from '@tanstack/react-query'
import { useServerFn } from '@tanstack/react-start'
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
} from './ui/dropdown-menu'
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar'
import { SidebarMenuButton, useSidebar } from './ui/sidebar'
import { logoutFn } from '#/lib/auth'
import { userMeQueryOptions } from '#/lib/user'
import ThemeToggle from './ThemeToggle'

export default function AppSidebarBottom() {
  const logout = useServerFn(logoutFn)

  const { isMobile } = useSidebar()
  const { data: user } = useSuspenseQuery(userMeQueryOptions())

  const wallet = useTonWallet()
  const [tonConnectUI] = useTonConnectUI()

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <SidebarMenuButton size="lg">
          <div className="font-semibold">{user.firstName}</div>
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
                <span className="truncate text-xs">@{user.username}</span>
              </div>
            </div>
          </DropdownMenuLabel>
          <ThemeToggle />
          {wallet === null ? (
            <DropdownMenuItem onClick={() => tonConnectUI.openModal()}>
              <PlugZapIcon /> Подключить кошелек
            </DropdownMenuItem>
          ) : (
            <DropdownMenuItem onClick={() => tonConnectUI.disconnect()}>
              <UnplugIcon /> Отключить кошелек
            </DropdownMenuItem>
          )}
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuGroup className="flex gap-1">
          <DropdownMenuItem
            className="flex-1 w-full"
            variant="destructive"
            onClick={async () => {
              await logout()
            }}
          >
            <LogOutIcon />
            Выйти
          </DropdownMenuItem>
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

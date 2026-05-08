import { useSuspenseQuery } from '@tanstack/react-query'
import { useServerFn } from '@tanstack/react-start'
import { ChevronsUpDownIcon, LogOutIcon } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu'
import { TonIcon } from './icons/TonIcon'
import { Button } from './ui/button'
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar'
import { SidebarMenuButton, useSidebar } from './ui/sidebar'
import { logoutFn } from '#/lib/auth'
import { userMeQueryOptions } from '#/lib/user'
import ThemeToggle from './ThemeToggle'

export default function AppSidebarBottom() {
  const logout = useServerFn(logoutFn)

  const { isMobile } = useSidebar()
  const { data: user } = useSuspenseQuery(userMeQueryOptions())

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
          <div className="text-sm flex items-center gap-1 py-2 px-1">
            Баланс:{' '}
            <span className="font-semibold flex gap-0.5 items-center">
              {user.balance.toFixed(2)} <TonIcon />
            </span>
          </div>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <ThemeToggle />
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuGroup className="flex gap-1">
          <Button
            className="flex-1 w-full"
            variant="destructive"
            onClick={async () => {
              await logout()
            }}
          >
            <LogOutIcon />
            Выйти
          </Button>
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

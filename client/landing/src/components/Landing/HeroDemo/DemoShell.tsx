import {
  ChevronsUpDownIcon,
  ExternalLinkIcon,
  HomeIcon,
  KeySquareIcon,
  ListIcon,
  PanelLeftIcon,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { TelegramLogoIcon } from '#/components/icons/TelegramLogoIcon'
import { cn } from '#/lib/utils'

function NavItem({
  icon: Icon,
  label,
  active = false,
}: {
  icon: LucideIcon
  label: string
  active?: boolean
}) {
  return (
    <div
      className={cn(
        'flex h-8 items-center gap-2 rounded-md px-2',
        active &&
          'bg-sidebar-accent text-sidebar-accent-foreground font-medium',
      )}
    >
      <Icon className="size-4 shrink-0" />
      <span className="truncate">{label}</span>
    </div>
  )
}

/** Static copy of the dashboard sidebar; the real one needs its provider. */
export function DemoSidebar() {
  return (
    <aside
      aria-hidden
      className="text-sidebar-foreground hidden w-52 shrink-0 flex-col p-2 md:flex"
    >
      <div className="flex flex-col gap-1 p-2">
        <NavItem icon={HomeIcon} label="Главная" active />
        <NavItem icon={ListIcon} label="Транзакции" />
        <NavItem icon={KeySquareIcon} label="API Токены" />
      </div>
      <div className="bg-sidebar-border mx-2 h-px" />
      <div className="p-2">
        <NavItem icon={ExternalLinkIcon} label="Документация" />
      </div>
      <div className="mt-auto flex h-12 items-center px-4 font-semibold">
        Synca
        <ChevronsUpDownIcon className="ml-auto size-4" />
      </div>
    </aside>
  )
}

export function DemoTopBar() {
  return (
    <div
      aria-hidden
      className="flex shrink-0 items-center justify-between border-b px-4 py-2.5"
    >
      <div className="flex items-center gap-4">
        <PanelLeftIcon className="size-4" />
        <span className="bg-border h-4 w-px" />
        <span className="text-base">Панель</span>
      </div>
      <span className="flex items-center gap-1 text-sm [&>svg]:size-4">
        Чат <TelegramLogoIcon />
      </span>
    </div>
  )
}

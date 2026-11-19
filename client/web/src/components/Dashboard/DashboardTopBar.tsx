import { siteConfig } from '#/config'
import { SidebarTrigger } from '../ui/sidebar'
import { m } from '#/paraglide/messages'
import { TelegramLogoIcon } from '../icons/TelegramLogoIcon'

export default function DashboardTopBar() {
  return (
    <div className="border-b">
      <div className="py-2 px-2 md:px-4 flex items-center justify-between w-full max-w-7xl mx-auto">
        <div className="flex items-center gap-2 md:gap-4">
          <SidebarTrigger className="px-2 py-2" />
          <hr className="h-4 w-px rounded-full bg-border" />
          <h4 className="text-base font-heading">{m.dashboard()}</h4>
        </div>
        <a
          className="flex items-center gap-1  text-sm font-normal hover:underline [&>svg]:size-4"
          href={siteConfig.telegramChat}
        >
          {m.chat()} <TelegramLogoIcon />
        </a>
      </div>
    </div>
  )
}

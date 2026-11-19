import { siteConfig } from '#/config'

export default function Footer() {
  const links = [
    { label: 'Документация', href: siteConfig.docs },
    { label: 'GitHub', href: siteConfig.github },
    {
      label: 'Telegram-канал',
      href: siteConfig.telegramChannel,
    },
    { label: 'Telegram-чат', href: siteConfig.telegramChat },
  ]

  return (
    <footer className="w-full px-4">
      <div className="mx-auto flex max-w-280 flex-col gap-8 pt-16 pb-12 sm:pt-24">
        <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
          <div className="flex flex-col gap-2">
            <span className="text-xl font-semibold tracking-[-0.01em]">
              FragAPI
            </span>
            <p className="text-muted-foreground text-sm leading-5.5">
              API для автоматизации Fragment.
              <br />
              Без KYC и seed фраз.
            </p>
          </div>
          <nav className="text-muted-foreground flex flex-wrap gap-x-8 gap-y-2 text-sm font-medium">
            {links.map((link) => (
              <a
                key={link.label}
                href={link.href}
                className="hover:text-foreground transition-colors"
              >
                {link.label}
              </a>
            ))}
          </nav>
        </div>
        <div className="bg-border h-px w-full" />
        <div className="text-muted-foreground flex justify-between gap-4 text-[13px] leading-5">
          <p>© {new Date().getFullYear()} FragAPI</p>
          <p>Лицензия MIT</p>
        </div>
      </div>
    </footer>
  )
}

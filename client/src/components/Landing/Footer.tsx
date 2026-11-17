import { siteConfig } from '#/config'
import { m } from '#/paraglide/messages'

export default function Footer() {
  const links = [
    { label: m.land_docs(), href: siteConfig.docs },
    { label: 'GitHub', href: siteConfig.github },
    {
      label: m.land_footer_telegram_channel(),
      href: siteConfig.telegramChannel,
    },
    { label: m.land_footer_telegram_chat(), href: siteConfig.telegramChat },
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
              {m.land_footer_tagline_line_1()}
              <br />
              {m.land_footer_tagline_line_2()}
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
          <p>{m.land_footer_license()}</p>
        </div>
      </div>
    </footer>
  )
}

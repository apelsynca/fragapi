import { LoginButton } from './LandingActions'
import { siteConfig } from '#/config'

export default function Header() {
  return (
    <header className="w-full px-4">
      <div className="mx-auto flex max-w-280 items-center justify-between pt-6">
        <span className="text-xl font-semibold tracking-[-0.01em]">
          FragAPI
        </span>
        <nav className="flex items-center gap-2">
          <div className="text-muted-foreground hidden gap-7 pr-5 text-sm font-medium sm:flex">
            <a
              href={siteConfig.docs}
              className="hover:text-foreground transition-colors"
            >
              Документация
            </a>
            <a
              href={siteConfig.github}
              className="hover:text-foreground transition-colors"
            >
              GitHub
            </a>
          </div>
          <LoginButton />
        </nav>
      </div>
    </header>
  )
}

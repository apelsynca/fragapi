import { DocsButton, GithubButton, LoginButton } from './LandingActions'
import { useScrollParallax } from '#/hooks/useScrollParallax'

export default function CTA() {
  const glowRef = useScrollParallax<HTMLDivElement>()

  return (
    <section className="w-full px-4">
      <div className="border-border relative mx-auto flex max-w-280 flex-col items-center gap-8 overflow-hidden rounded-3xl border bg-white/2 px-6 pt-16 pb-18 sm:pt-22 sm:pb-24">
        <div
          ref={glowRef}
          aria-hidden
          className="from-brand-foreground/50 pointer-events-none absolute top-[56%] left-1/2 h-155 w-[125%] -translate-x-1/2 translate-y-[var(--parallax-y,0px)] rounded-[50%] bg-radial-[closest-side] from-15% to-transparent to-85% opacity-80"
        />
        <div className="relative flex flex-col items-center gap-4 text-center">
          <h2 className="text-3xl font-semibold tracking-[-0.02em] sm:text-5xl sm:leading-14">
            Автоматизируйте Fragment
            <br />
            уже сегодня
          </h2>
          <p className="text-muted-foreground max-w-140 text-lg leading-7">
            Войдите через Telegram-бота, пополните баланс и отправьте первый
            запрос уже через пару минут.
          </p>
        </div>
        <div className="relative flex flex-wrap justify-center gap-2">
          <LoginButton />
          <DocsButton />
          <GithubButton />
        </div>
      </div>
    </section>
  )
}

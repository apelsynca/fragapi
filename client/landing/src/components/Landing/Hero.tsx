import {
  KeyRoundIcon,
  PercentIcon,
  ServerIcon,
  ShieldCheckIcon,
} from 'lucide-react'
import HeroDemo from './HeroDemo'
import HeroField from './HeroField'
import { DocsButton, GithubButton, LoginButton } from './LandingActions'
import { Mockup, MockupFrame } from '#/components/ui/mockup'
import { useScrollTilt } from '#/hooks/useScrollTilt'

export default function Hero() {
  const tiltRef = useScrollTilt<HTMLDivElement>()

  const chips = [
    { icon: ShieldCheckIcon, label: 'Без KYC' },
    { icon: KeyRoundIcon, label: 'Без seed фраз' },
    { icon: PercentIcon, label: 'Комиссия 1.8%' },
    { icon: ServerIcon, label: 'Можно развернуть у себя' },
  ]

  return (
    // Clipped sideways only, with no bottom rule: the field runs on past the
    // hero and fades out over the next section.
    <section className="relative w-full overflow-x-clip px-4 pt-12 sm:pt-22">
      <HeroField className="text-brand-foreground pointer-events-none absolute inset-x-0 top-0 h-[calc(100%+12rem)] w-full mask-[linear-gradient(to_bottom,transparent,rgb(0_0_0/0.3)_8%,black_25%,black_55%,transparent)] font-mono opacity-0 transition-opacity duration-300 [--field-strong:var(--foreground)] data-ready:opacity-100" />
      <div className="max-w-container relative mx-auto flex flex-col items-center text-center">
        <div className="animate-appear border-border text-muted-foreground relative z-10 flex items-center gap-2 rounded-full border bg-white/4 py-1.5 pr-3.5 pl-3 text-[13px] leading-5 font-medium">
          <span className="bg-brand size-2 rounded-full" />
          Открытый исходный код · MIT
        </div>
        <h1 className="animate-appear from-foreground to-foreground dark:to-muted-foreground relative z-10 mt-6 bg-linear-to-r bg-clip-text text-4xl leading-tight font-semibold tracking-[-0.035em] text-balance text-transparent drop-shadow-2xl sm:text-6xl sm:leading-[1.06] lg:text-[68px]">
          Автоматизируйте Fragment
          <br />
          через простой API
        </h1>
        <p className="animate-appear text-muted-foreground relative z-10 mt-5 max-w-170 text-base font-medium text-balance opacity-0 delay-100 sm:text-xl sm:leading-7">
          Покупайте Telegram Stars и Premium одним запросом. Без KYC, без ввода
          seed фраз, с полностью открытым исходным кодом.
        </p>
        <div className="animate-appear relative z-10 mt-8 flex flex-wrap justify-center gap-2 opacity-0 delay-300">
          <LoginButton />
          <DocsButton />
          <GithubButton />
        </div>
        <ul className="animate-appear text-muted-foreground relative z-10 mt-7 flex flex-wrap justify-center gap-2 text-[13px] font-medium opacity-0 delay-500">
          {chips.map(({ icon: Icon, label }) => (
            <li
              key={label}
              className="flex h-8 items-center gap-2 rounded-full bg-white/4 px-3"
            >
              <Icon className="size-3.5" />
              {label}
            </li>
          ))}
        </ul>
        <div className="relative mt-8 w-full pt-8 sm:mt-12">
          {/* Appear and tilt sit on separate elements: both animate
              `transform`. */}
          <div className="animate-appear relative z-10 mask-[linear-gradient(to_top,transparent,black_18%)] opacity-0 delay-700">
            <div
              ref={tiltRef}
              className="relative transform-[perspective(1400px)_translateY(calc(var(--tilt,1)*24px))_rotateX(calc(var(--tilt,1)*16deg))_scale(calc(1_-_var(--tilt,1)*0.08))] motion-reduce:transform-none"
            >
              <div
                aria-hidden
                className="pointer-events-none absolute inset-x-0 top-0 z-20"
              >
                <div className="bg-brand-foreground/50 absolute top-0 left-1/2 h-10 w-3/5 -translate-x-1/2 -translate-y-1/2 rounded-[50%] blur-2xl" />
                <div className="via-brand absolute inset-x-[12%] top-0 h-px bg-linear-to-r from-transparent to-transparent" />
              </div>
              <MockupFrame size="small">
                <Mockup
                  type="responsive"
                  className="bg-background/90 w-full rounded-xl border-0"
                >
                  <HeroDemo />
                </Mockup>
              </MockupFrame>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

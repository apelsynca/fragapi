import { DocsButton, GithubButton, LoginButton } from './LandingActions'
import Glow from '#/components/ui/glow'
import { Mockup, MockupFrame } from '#/components/ui/mockup'
import Screenshot from '#/components/ui/screenshot'
import { useScrollParallax } from '#/hooks/useScrollParallax'
import { m } from '#/paraglide/messages'

export default function Hero({ toPanel = false }: { toPanel?: boolean }) {
  const glowRef = useScrollParallax<HTMLDivElement>()

  return (
    <section className="line-b fade-bottom w-full overflow-hidden px-4 pt-12 sm:pt-22">
      <div className="max-w-container mx-auto flex flex-col items-center gap-8 text-center">
        <div className="animate-appear border-border text-muted-foreground relative z-10 flex items-center gap-2 rounded-full border bg-white/4 py-1.5 pr-3.5 pl-3 text-[13px] leading-5 font-medium">
          <span className="bg-brand size-2 rounded-full" />
          {m.land_badge()}
        </div>
        <h1 className="animate-appear from-foreground to-foreground dark:to-muted-foreground relative z-10 bg-linear-to-r bg-clip-text text-4xl leading-tight font-semibold tracking-[-0.025em] text-transparent drop-shadow-2xl sm:text-6xl sm:leading-tight lg:text-[76px] lg:leading-22">
          {m.land_title_line_1()}
          <br />
          {m.land_title_line_2()}
        </h1>
        <p className="animate-appear text-muted-foreground relative z-10 max-w-170 text-base font-medium text-balance opacity-0 delay-100 sm:text-xl sm:leading-7">
          {m.land_description()}
        </p>
        <div className="animate-appear relative z-10 flex flex-wrap justify-center gap-2 opacity-0 delay-300">
          <LoginButton toPanel={toPanel} />
          <DocsButton />
          <GithubButton />
        </div>
        <div className="relative w-full pt-8">
          <MockupFrame
            className="animate-appear opacity-0 delay-700"
            size="small"
          >
            <Mockup
              type="responsive"
              className="bg-background/90 w-full rounded-xl border-0"
            >
              <Screenshot
                srcLight="/dashboard-light.png"
                srcDark="/dashboard-dark.png"
                alt="FragAPI Dashboard screenshot"
                width={1248}
                height={765}
                className="w-full"
              />
            </Mockup>
          </MockupFrame>
          {/* The drift sits on a wrapper: Chrome does not re-resolve
              --parallax-y on the element running the appear animation. */}
          <div
            ref={glowRef}
            className="pointer-events-none absolute inset-x-0 top-0 translate-y-[var(--parallax-y,0px)]"
          >
            <Glow
              variant="top"
              className="animate-appear-zoom opacity-0 delay-1000"
            />
          </div>
        </div>
      </div>
    </section>
  )
}

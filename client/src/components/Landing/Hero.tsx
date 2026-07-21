import { BotIcon, ExternalLinkIcon, LogInIcon } from 'lucide-react'
import { Link } from '@tanstack/react-router'
import Glow from '#/components/ui/glow'
import { Mockup, MockupFrame } from '#/components/ui/mockup'
import Screenshot from '#/components/ui/screenshot'
import { Section } from '#/components/ui/section'
import { Button } from '#/components/ui/button'
import { GithubLogoIcon } from '#/components/icons/GithubLogoIcon'
import { cn } from '#/lib/utils'
import { siteConfig } from '#/config'
import { m } from '#/paraglide/messages'

interface HeroProps {
  title?: string
  description?: string
  badge?: React.ReactNode
  className?: string
  toPanel?: boolean
}

export default function Hero({
  title,
  description,
  badge = false,
  toPanel = false,
  className,
}: HeroProps) {
  return (
    <Section
      className={cn(
        'fade-bottom overflow-hidden pb-0 sm:pb-0 md:pb-0',
        className,
      )}
    >
      <div className="max-w-container mx-auto flex flex-col gap-12 pt-16 sm:gap-24">
        <div className="flex flex-col items-center gap-6 text-center sm:gap-12">
          {badge != false && badge}
          <h1 className="animate-appear from-foreground to-foreground dark:to-muted-foreground relative z-10 inline-block bg-linear-to-r bg-clip-text text-4xl leading-tight font-semibold text-balance text-transparent drop-shadow-2xl sm:text-6xl sm:leading-tight md:text-8xl md:leading-tight">
            {title}
          </h1>
          <p className="text-md animate-appear text-muted-foreground relative z-10 max-w-185 font-medium text-balance opacity-0 delay-100 sm:text-xl">
            {description}
          </p>
          <div className="animate-appear relative z-10 flex flex-col gap-2 opacity-0 delay-300">
            <div>
              {toPanel ? (
                <Button asChild size="lg" className="w-full">
                  <Link to="/dashboard">
                    <LogInIcon /> {m.land_go_to_panel()}
                  </Link>
                </Button>
              ) : (
                <Button asChild size="lg" className="w-full">
                  <a
                    href={`https://t.me/${siteConfig.botUsername}?start=login`}
                  >
                    <BotIcon /> {m.land_bot_login()}
                  </a>
                </Button>
              )}
            </div>

            <div className="flex gap-2">
              <Button variant="secondary" size="lg" asChild>
                <a href={siteConfig.docs}>
                  <ExternalLinkIcon /> Documentation
                </a>
              </Button>
              <Button variant="secondary" size="lg" asChild>
                <a href={siteConfig.github}>
                  <GithubLogoIcon /> GitHub
                </a>
              </Button>
            </div>
          </div>
          <div className="relative w-full pt-12">
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
            <Glow
              variant="top"
              className="animate-appear-zoom opacity-0 delay-1000"
            />
          </div>
        </div>
      </div>
    </Section>
  )
}

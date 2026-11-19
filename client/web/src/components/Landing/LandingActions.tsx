import { BotIcon, ExternalLinkIcon, LogInIcon } from 'lucide-react'
import { Link } from '@tanstack/react-router'
import { Button } from '#/components/ui/button'
import { GithubLogoIcon } from '#/components/icons/GithubLogoIcon'
import { siteConfig } from '#/config'
import { useBotLoginLink } from '#/hooks/useBotLoginLink'
import { m } from '#/paraglide/messages'

interface ActionProps {
  className?: string
}

export function LoginButton({
  toPanel = false,
  className,
}: ActionProps & { toPanel?: boolean }) {
  const href = useBotLoginLink()
  return (
    <Button asChild size="lg" className={className}>
      {toPanel ? (
        <Link to="/dashboard">
          <LogInIcon /> {m.land_go_to_panel()}
        </Link>
      ) : (
        <a href={href}>
          <BotIcon /> {m.land_bot_login()}
        </a>
      )}
    </Button>
  )
}

export function DocsButton({ className }: ActionProps) {
  return (
    <Button variant="secondary" size="lg" asChild className={className}>
      <a href={siteConfig.docs}>
        <ExternalLinkIcon /> {m.land_docs()}
      </a>
    </Button>
  )
}

export function GithubButton({
  label = 'GitHub',
  className,
}: ActionProps & { label?: string }) {
  return (
    <Button variant="secondary" size="lg" asChild className={className}>
      <a href={siteConfig.github}>
        <GithubLogoIcon size={16} /> {label}
      </a>
    </Button>
  )
}

import { BotIcon, ExternalLinkIcon } from 'lucide-react'
import { Button } from '#/components/ui/button'
import { GithubLogoIcon } from '#/components/icons/GithubLogoIcon'
import { siteConfig } from '#/config'

interface ActionProps {
  className?: string
}

export function LoginButton({ className }: ActionProps) {
  return (
    <Button asChild size="lg" className={className}>
      <a href={`https://t.me/${siteConfig.botUsername}?start=login`}>
        <BotIcon /> Войти через Бота
      </a>
    </Button>
  )
}

export function DocsButton({ className }: ActionProps) {
  return (
    <Button variant="secondary" size="lg" asChild className={className}>
      <a href={siteConfig.docs}>
        <ExternalLinkIcon /> Документация
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

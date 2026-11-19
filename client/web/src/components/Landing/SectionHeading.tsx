import { cn } from '#/lib/utils'

interface SectionHeadingProps {
  eyebrow: string
  title: string
  subtitle?: string
  align?: 'center' | 'start'
  className?: string
}

export default function SectionHeading({
  eyebrow,
  title,
  subtitle,
  align = 'center',
  className,
}: SectionHeadingProps) {
  return (
    <div
      className={cn(
        'flex flex-col gap-4',
        align === 'center' && 'items-center text-center',
        className,
      )}
    >
      <p className="text-brand text-sm font-medium">{eyebrow}</p>
      <h2 className="text-3xl font-semibold tracking-[-0.02em] sm:text-5xl sm:leading-14">
        {title}
      </h2>
      {subtitle && (
        <p className="text-muted-foreground max-w-150 text-lg leading-7">
          {subtitle}
        </p>
      )}
    </div>
  )
}

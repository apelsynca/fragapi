import { cn } from '#/lib/utils'

interface ScreenshotProps {
  srcLight: string
  srcDark?: string
  alt: string
  width: number
  height: number
  className?: string
}

export default function Screenshot({
  srcLight,
  srcDark,
  alt,
  width,
  height,
  className,
}: ScreenshotProps) {
  if (!srcDark) {
    return (
      <img
        src={srcLight}
        alt={alt}
        width={width}
        height={height}
        className={className}
      />
    )
  }

  return (
    <>
      <img
        src={srcLight}
        alt={alt}
        width={width}
        height={height}
        className={cn(className, 'block dark:hidden')}
      />
      <img
        src={srcDark}
        alt={alt}
        width={width}
        height={height}
        className={cn(className, 'hidden dark:block')}
      />
    </>
  )
}

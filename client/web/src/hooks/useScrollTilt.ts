import { useEffect, useRef } from 'react'

/**
 * Lays an element flat as it scrolls up the viewport: writes a 1 → 0 progress
 * to the `--tilt` CSS variable, which the element's transform consumes. The
 * element is fully tilted while its top is below `from` of the viewport height
 * and flat once it is above `to`.
 */
export function useScrollTilt<T extends HTMLElement>(from = 0.6, to = 0.12) {
  const ref = useRef<T>(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return

    let frame = 0

    const update = () => {
      frame = 0
      // The parent does not move with the tilt, so it gives a stable reading.
      const top = (el.parentElement ?? el).getBoundingClientRect().top
      const progress = (top / window.innerHeight - to) / (from - to)
      el.style.setProperty(
        '--tilt',
        Math.max(0, Math.min(1, progress)).toFixed(3),
      )
    }

    const schedule = () => {
      if (frame === 0) frame = requestAnimationFrame(update)
    }

    update()
    window.addEventListener('scroll', schedule, { passive: true })
    window.addEventListener('resize', schedule)

    return () => {
      cancelAnimationFrame(frame)
      window.removeEventListener('scroll', schedule)
      window.removeEventListener('resize', schedule)
      el.style.removeProperty('--tilt')
    }
  }, [from, to])

  return ref
}

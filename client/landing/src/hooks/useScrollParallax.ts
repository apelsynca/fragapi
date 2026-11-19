import { useEffect, useRef } from 'react'

/**
 * Drifts an element against the scroll: writes its vertical offset to the
 * `--parallax-y` CSS variable, which the element consumes with
 * `translate-y-[var(--parallax-y,0px)]`. The offset is zero when the element
 * sits at the viewport centre and is capped at `maxPx` either way.
 */
export function useScrollParallax<T extends HTMLElement>(
  factor = 0.35,
  maxPx = 200,
) {
  const ref = useRef<T>(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return

    let frame = 0
    let offset = 0

    const update = () => {
      frame = 0
      const rect = el.getBoundingClientRect()
      // Where the element would sit without the offset applied so far.
      const restCentre = rect.top + rect.height / 2 - offset
      const fromCentre = restCentre - window.innerHeight / 2
      offset = Math.max(-maxPx, Math.min(maxPx, -fromCentre * factor))
      el.style.setProperty('--parallax-y', `${offset.toFixed(1)}px`)
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
      el.style.removeProperty('--parallax-y')
    }
  }, [factor, maxPx])

  return ref
}

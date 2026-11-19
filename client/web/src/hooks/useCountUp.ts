import { useEffect, useRef, useState } from 'react'

/**
 * Starts at `target` (so SSR shows the real number) and eases to every later
 * `target` instead of jumping.
 */
export function useCountUp(target: number, durationMs = 1200) {
  const [value, setValue] = useState(target)
  const shownRef = useRef(target)

  useEffect(() => {
    const from = shownRef.current
    if (from === target) return

    const duration = window.matchMedia('(prefers-reduced-motion: reduce)')
      .matches
      ? 0
      : durationMs
    const startedAt = performance.now()
    let frame = 0

    const tick = (now: number) => {
      const progress =
        duration === 0 ? 1 : Math.min((now - startedAt) / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      const current = Math.round(from + (target - from) * eased)

      shownRef.current = current
      setValue(current)

      if (progress < 1) frame = requestAnimationFrame(tick)
    }

    frame = requestAnimationFrame(tick)

    return () => cancelAnimationFrame(frame)
  }, [target, durationMs])

  return value
}

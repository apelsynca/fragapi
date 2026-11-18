import { useCallback, useEffect, useReducer, useRef, useState } from 'react'
import { demoReducer, initialDemoState } from './demoState'

const IDLE_MS = 2400
const SENDING_MS = 900
const DONE_MS = 2800

/**
 * Drives the demo: a request goes out, lands, and the next one is queued.
 * Requests fire on their own only while the demo is on screen and motion is
 * allowed; `send` fires one by hand either way.
 */
export function useDemoLoop<T extends HTMLElement>() {
  const ref = useRef<T>(null)
  const [state, dispatch] = useReducer(demoReducer, initialDemoState)
  const [auto, setAuto] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return

    const observer = new IntersectionObserver(
      ([entry]) => setAuto(entry.isIntersecting),
      { threshold: 0.2 },
    )
    observer.observe(el)

    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    if (state.phase === 'idle' && !auto) return

    const timer =
      state.phase === 'idle'
        ? setTimeout(() => dispatch({ type: 'send' }), IDLE_MS)
        : state.phase === 'sending'
          ? setTimeout(() => dispatch({ type: 'complete' }), SENDING_MS)
          : setTimeout(() => dispatch({ type: 'next' }), DONE_MS)

    return () => clearTimeout(timer)
  }, [state.phase, state.step, auto])

  const send = useCallback(() => dispatch({ type: 'send' }), [])

  return { ref, state, send }
}

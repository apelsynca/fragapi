import { useEffect, useRef } from 'react'

/** Sparse to dense; a cell's value picks its character. */
const RAMP = ' :-=+*#%@'
const CELL_X = 12
const CELL_Y = 18
const FRAME_MS = 1000 / 12
const MAX_PIXEL_RATIO = 2

/** Hot spots that wander around a home position, in fractions of the canvas. */
const BLOBS = [
  { x: 0.13, y: 0.24, drift: 0.11, phase: 0 },
  { x: 0.86, y: 0.42, drift: 0.09, phase: 2.1 },
  { x: 0.03, y: 0.76, drift: 0.07, phase: 4.4 },
]

function smoothstep(from: number, to: number, value: number) {
  const t = Math.max(0, Math.min(1, (value - from) / (to - from)))
  return t * t * (3 - 2 * t)
}

/** Field density (0–1) at a point in CSS pixels, `time` in seconds. */
function density(
  x: number,
  y: number,
  width: number,
  height: number,
  time: number,
) {
  // Faint horizontal bands everywhere.
  const bands =
    0.1 +
    0.2 *
      (0.5 + 0.5 * Math.sin(y * 0.045 + 3 * Math.sin(x * 0.006 + time * 0.1)))

  const radius = Math.max(80, Math.min(190, width * 0.1))
  let blobs = 0
  for (const blob of BLOBS) {
    const dx =
      x - width * (blob.x + 0.04 * Math.sin(time * blob.drift + blob.phase))
    const dy =
      y -
      height * (blob.y + 0.06 * Math.cos(time * blob.drift * 1.3 + blob.phase))
    blobs += Math.exp(-(dx * dx + dy * dy) / (radius * radius))
  }

  const grain =
    0.5 +
    0.5 *
      Math.sin(x * 0.045 + 2 * Math.sin(y * 0.03 + time * 0.3) + time * 0.4) *
      Math.sin(y * 0.06 - time * 0.25)

  // Empty down the middle, where the hero copy and the demo sit.
  const edge = smoothstep(0.1, 0.42, Math.abs(x / width - 0.5))

  return Math.min(1, (bands + blobs * (0.5 + 0.5 * grain)) * edge)
}

/**
 * Drifting field of characters behind the hero. Drawn in the element's text
 * colour; pauses while off screen and holds a single frame when motion is
 * reduced.
 */
export default function HeroField({ className }: { className?: string }) {
  const ref = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = ref.current
    const context = canvas?.getContext('2d')
    if (!canvas || !context) return

    const reduced = window.matchMedia(
      '(prefers-reduced-motion: reduce)',
    ).matches
    let width = 0
    let height = 0
    let frame = 0
    let lastDraw = -Infinity
    let visible = true

    const draw = (now: number) => {
      const time = 40 + now / 1000
      const ratio = canvas.width / width
      // Narrow screens have the copy running edge to edge over the field.
      const dim = width < 640 ? 0.5 : 1

      context.setTransform(ratio, 0, 0, ratio, 0, 0)
      context.clearRect(0, 0, width, height)
      context.font = `13px ${getComputedStyle(canvas).fontFamily}`
      context.textBaseline = 'middle'
      context.textAlign = 'center'
      context.fillStyle = getComputedStyle(canvas).color

      for (let y = CELL_Y / 2; y < height; y += CELL_Y) {
        for (let x = CELL_X / 2; x < width; x += CELL_X) {
          const value = density(x, y, width, height, time)
          const level = Math.min(
            RAMP.length - 1,
            Math.floor(value * RAMP.length),
          )
          if (level === 0) continue

          context.globalAlpha = dim * (0.1 + 0.55 * value * value)
          context.fillText(RAMP[level], x, y)
        }
      }

      canvas.dataset.ready = ''
    }

    const tick = (now: number) => {
      frame = requestAnimationFrame(tick)
      if (now - lastDraw < FRAME_MS) return
      lastDraw = now
      draw(now)
    }

    const start = () => {
      cancelAnimationFrame(frame)
      if (width === 0 || height === 0) return
      if (reduced) draw(0)
      else if (visible) frame = requestAnimationFrame(tick)
    }

    const resizeObserver = new ResizeObserver(() => {
      const ratio = Math.min(window.devicePixelRatio, MAX_PIXEL_RATIO)
      width = canvas.clientWidth
      height = canvas.clientHeight
      canvas.width = Math.round(width * ratio)
      canvas.height = Math.round(height * ratio)
      lastDraw = -Infinity
      start()
    })
    resizeObserver.observe(canvas)

    const intersectionObserver = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting
      start()
    })
    intersectionObserver.observe(canvas)

    return () => {
      cancelAnimationFrame(frame)
      resizeObserver.disconnect()
      intersectionObserver.disconnect()
    }
  }, [])

  return <canvas ref={ref} aria-hidden className={className} />
}

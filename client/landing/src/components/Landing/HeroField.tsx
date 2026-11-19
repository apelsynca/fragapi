import { useEffect, useRef } from 'react'

/** Sparse to dense; a cell's value picks its character. */
const RAMP = ' :-=+*#%@'
const CELL_X = 12
const CELL_Y = 18
const FRAME_MS = 1000 / 12
/** Frame interval while the intro or the pointer trail is animating. */
const ACTIVE_FRAME_MS = 1000 / 30
const MAX_PIXEL_RATIO = 2

/** Radius of the pointer highlight, in CSS pixels. */
const POINTER_RADIUS = 110
/** How quickly the highlight catches up with the pointer, per 30 fps frame. */
const POINTER_EASE = 0.22
/** Time constant of the trail the pointer leaves behind. */
const TRAIL_FADE_MS = 380
/** Above this a cell is drawn bold, in the strong colour. */
const STRONG_THRESHOLD = 0.25

/** Length of the reveal that sweeps out from the top centre on load. */
const INTRO_MS = 1800
/** Width of the reveal's leading edge, as a fraction of the sweep. */
const INTRO_FRONT = 0.22
/** How ragged that edge is, as a fraction of the sweep. */
const INTRO_JITTER = 0.12

/** Hot spots that wander around a home position, in fractions of the canvas. */
const BLOBS = [
  { x: 0.13, y: 0.24, drift: 0.11, phase: 0 },
  { x: 0.86, y: 0.42, drift: 0.09, phase: 2.1 },
  { x: 0.03, y: 0.76, drift: 0.07, phase: 4.4 },
]

function clamp01(value: number) {
  return Math.max(0, Math.min(1, value))
}

function smoothstep(from: number, to: number, value: number) {
  const t = clamp01((value - from) / (to - from))
  return t * t * (3 - 2 * t)
}

/** Stable pseudo-random number (0–1) for a cell. */
function hash(column: number, row: number) {
  const value = Math.sin(column * 12.9898 + row * 78.233) * 43758.5453
  return value - Math.floor(value)
}

/**
 * 0 down the middle, where the hero copy and the demo sit, rising to 1 at the
 * sides.
 */
function clearing(x: number, width: number) {
  return smoothstep(0.1, 0.42, Math.abs(x / width - 0.5))
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

  return Math.min(1, bands + blobs * (0.5 + 0.5 * grain))
}

/**
 * Drifting field of characters behind the hero. Drawn in the element's text
 * colour; cells near the pointer, and on the leading edge of the reveal that
 * plays on load, turn denser and bold in `--field-strong`. Pauses while off
 * screen and holds a single frame when motion is reduced.
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
    const coarse = window.matchMedia('(pointer: coarse)').matches

    let width = 0
    let height = 0
    let columns = 0
    let rows = 0
    let frame = 0
    let lastDraw = -Infinity
    let visible = true
    /** Still animating faster than the idle drift needs. */
    let active = true
    let introStart: number | null = null

    /** Per-cell highlight left by the pointer, 0–1. */
    let trail = new Float32Array(0)
    /** Pointer in viewport coordinates, or null when it is off the page. */
    let pointer: { x: number; y: number } | null = null
    /** Eased highlight position in canvas coordinates. */
    let spot: { x: number; y: number } | null = null
    /** Flat [x, y, level, alpha] runs for the bold pass. */
    const strong: Array<number> = []

    const updateTrail = (elapsed: number) => {
      let live = false
      const fade = Math.exp(-elapsed / TRAIL_FADE_MS)
      for (let index = 0; index < trail.length; index++) {
        const value = trail[index] * fade
        if (value > 0.004) {
          trail[index] = value
          live = true
        } else {
          trail[index] = 0
        }
      }

      if (!pointer) {
        spot = null
        return live
      }
      const rect = canvas.getBoundingClientRect()
      const x = pointer.x - rect.left
      const y = pointer.y - rect.top
      if (x < 0 || y < 0 || x > width || y > height) {
        spot = null
        return live
      }

      if (spot) {
        const ease = 1 - (1 - POINTER_EASE) ** (elapsed / ACTIVE_FRAME_MS)
        spot.x += (x - spot.x) * ease
        spot.y += (y - spot.y) * ease
      } else {
        spot = { x, y }
      }

      const firstColumn = Math.max(
        0,
        Math.floor((spot.x - POINTER_RADIUS) / CELL_X),
      )
      const lastColumn = Math.min(
        columns - 1,
        Math.ceil((spot.x + POINTER_RADIUS) / CELL_X),
      )
      const firstRow = Math.max(
        0,
        Math.floor((spot.y - POINTER_RADIUS) / CELL_Y),
      )
      const lastRow = Math.min(
        rows - 1,
        Math.ceil((spot.y + POINTER_RADIUS) / CELL_Y),
      )
      for (let row = firstRow; row <= lastRow; row++) {
        for (let column = firstColumn; column <= lastColumn; column++) {
          const dx = (column + 0.5) * CELL_X - spot.x
          const dy = (row + 0.5) * CELL_Y - spot.y
          const falloff = 1 - Math.hypot(dx, dy) / POINTER_RADIUS
          if (falloff <= 0) continue
          const index = row * columns + column
          trail[index] = Math.max(trail[index], falloff * falloff)
        }
      }
      return true
    }

    const draw = (now: number, elapsed: number) => {
      const time = 40 + now / 1000
      const ratio = canvas.width / width
      // Narrow screens have the copy running edge to edge over the field.
      const dim = width < 640 ? 0.5 : 1

      const trailLive = reduced ? false : updateTrail(elapsed)

      let intro = 1
      if (!reduced) {
        introStart ??= now
        intro = clamp01((now - introStart) / INTRO_MS)
      }
      // The front overshoots so the last cells finish resolving.
      const front =
        (1 - (1 - intro) ** 3) * (1 + INTRO_FRONT + INTRO_JITTER + 0.01)
      const reach = Math.hypot(width / 2, height)
      active = trailLive || intro < 1

      const style = getComputedStyle(canvas)
      const font = `13px ${style.fontFamily}`
      const strongColor =
        style.getPropertyValue('--field-strong').trim() || style.color

      context.setTransform(ratio, 0, 0, ratio, 0, 0)
      context.clearRect(0, 0, width, height)
      context.font = font
      context.textBaseline = 'middle'
      context.textAlign = 'center'
      context.fillStyle = style.color
      strong.length = 0

      for (let row = 0; row < rows; row++) {
        const y = (row + 0.5) * CELL_Y
        for (let column = 0; column < columns; column++) {
          const x = (column + 0.5) * CELL_X
          const clear = clearing(x, width)
          if (clear === 0) continue

          let value = density(x, y, width, height, time) * clear
          let highlight = trail[row * columns + column] * clear

          if (intro < 1) {
            const distance = Math.hypot(x - width / 2, y) / reach
            const reveal = clamp01(
              (front - distance - INTRO_JITTER * hash(column, row)) /
                INTRO_FRONT,
            )
            if (reveal === 0) continue
            // Peaks halfway through a cell's reveal: the bright leading edge.
            const edge = 4 * reveal * (1 - reveal)
            value *= reveal * reveal * (3 - 2 * reveal)
            highlight = Math.max(highlight, edge * Math.min(1, value * 4))
            value += edge * 0.25 * clear
          }

          value = Math.min(1, value + highlight * 0.9)
          const level = Math.min(
            RAMP.length - 1,
            Math.floor(value * RAMP.length),
          )
          if (level === 0) continue

          const alpha = Math.min(
            1,
            dim * (0.1 + 0.55 * value * value + 0.6 * highlight),
          )
          if (highlight > STRONG_THRESHOLD) {
            strong.push(x, y, level, alpha)
            continue
          }
          context.globalAlpha = alpha
          context.fillText(RAMP[level], x, y)
        }
      }

      if (strong.length > 0) {
        context.font = `bold ${font}`
        context.fillStyle = strongColor
        for (let index = 0; index < strong.length; index += 4) {
          context.globalAlpha = strong[index + 3]
          context.fillText(
            RAMP[strong[index + 2]],
            strong[index],
            strong[index + 1],
          )
        }
      }

      canvas.dataset.ready = ''
    }

    const tick = (now: number) => {
      frame = requestAnimationFrame(tick)
      const since = now - lastDraw
      if (since < (active ? ACTIVE_FRAME_MS : FRAME_MS)) return
      lastDraw = now
      // Capped so the trail does not jump after a pause.
      draw(now, Math.min(since, 100))
    }

    const start = () => {
      cancelAnimationFrame(frame)
      if (width === 0 || height === 0) return
      if (reduced) draw(0, 0)
      else if (visible) frame = requestAnimationFrame(tick)
    }

    const resizeObserver = new ResizeObserver(() => {
      const ratio = Math.min(window.devicePixelRatio, MAX_PIXEL_RATIO)
      width = canvas.clientWidth
      height = canvas.clientHeight
      columns = Math.ceil(width / CELL_X)
      rows = Math.ceil(height / CELL_Y)
      trail = new Float32Array(columns * rows)
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

    // The canvas sits behind the hero content and takes no pointer events,
    // so the pointer is tracked on the window.
    const onPointerMove = (event: PointerEvent) => {
      pointer = { x: event.clientX, y: event.clientY }
      active = true
    }
    const onPointerLeave = () => {
      pointer = null
    }
    const interactive = !reduced && !coarse
    if (interactive) {
      window.addEventListener('pointermove', onPointerMove, { passive: true })
      document.documentElement.addEventListener('pointerleave', onPointerLeave)
    }

    return () => {
      cancelAnimationFrame(frame)
      resizeObserver.disconnect()
      intersectionObserver.disconnect()
      window.removeEventListener('pointermove', onPointerMove)
      document.documentElement.removeEventListener(
        'pointerleave',
        onPointerLeave,
      )
    }
  }, [])

  return <canvas ref={ref} aria-hidden className={className} />
}

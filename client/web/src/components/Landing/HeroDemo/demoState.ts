/**
 * Everything the hero demo shows is scripted and deterministic: no clock and
 * no randomness, so the server render and the first client render match.
 */

export type PurchaseKind = 'stars' | 'premium'

export interface DemoPurchase {
  kind: PurchaseKind
  username: string
  name: string
  /** Stars for a stars purchase, months for a premium one. */
  quantity: number
  /** Price in TON. */
  amount: number
}

export interface DemoRow {
  id: number
  purchase: DemoPurchase
}

export interface ChartPoint {
  stars: number
  premium: number
}

export type DemoPhase = 'idle' | 'sending' | 'done'

export interface DemoState {
  phase: DemoPhase
  /** Index of the purchase the API panel is showing. */
  step: number
  rows: DemoRow[]
  balance: number
  starsSpend: number
  premiumSpend: number
  chart: ChartPoint[]
}

export type DemoAction =
  | { type: 'send' }
  | { type: 'complete' }
  | { type: 'next' }

export const TON_RATE = 1.74
export const CHART_MAX = 40

const VISIBLE_ROWS = 6
const LOW_BALANCE = 30
const TOP_UP = 200

const PURCHASES: DemoPurchase[] = [
  {
    kind: 'stars',
    username: 'synca',
    name: 'Synca',
    quantity: 50,
    amount: 0.39,
  },
  {
    kind: 'premium',
    username: 'alice',
    name: 'Alice',
    quantity: 3,
    amount: 6.9,
  },
  {
    kind: 'stars',
    username: 'shop_bot',
    name: 'Shop Bot',
    quantity: 500,
    amount: 3.9,
  },
  {
    kind: 'stars',
    username: 'maria',
    name: 'Maria',
    quantity: 100,
    amount: 0.78,
  },
  {
    kind: 'premium',
    username: 'bob_dev',
    name: 'Bob',
    quantity: 12,
    amount: 16.7,
  },
  { kind: 'stars', username: 'neo', name: 'Neo', quantity: 1000, amount: 7.8 },
]

const CHART_SEED: ChartPoint[] = [
  [4, 0],
  [9, 7],
  [6, 0],
  [14, 0],
  [11, 9],
  [5, 0],
  [18, 0],
  [22, 17],
  [12, 7],
  [8, 0],
  [16, 0],
  [25, 9],
  [19, 0],
  [10, 7],
  [7, 0],
  [21, 17],
  [28, 9],
  [15, 0],
  [13, 7],
  [24, 0],
  [30, 17],
  [17, 9],
  [20, 0],
  [9, 3],
].map(([stars, premium]) => ({ stars, premium }))

export function purchaseAt(step: number): DemoPurchase {
  return PURCHASES[step % PURCHASES.length]
}

/** Rows that came before the demo started carry negative ids. */
export function isNewRow(row: DemoRow) {
  return row.id >= 0
}

export function rowTime(id: number) {
  const seconds = 12 * 3600 + 4 * 60 + 10 + id * 37
  const part = (value: number) => String(value % 60).padStart(2, '0')

  return `${Math.floor(seconds / 3600)}:${part(Math.floor(seconds / 60))}:${part(seconds)}`
}

export function transactionId(id: number) {
  return `8f14e45f-ceea-467f-a0e6-${(0x1b2c3d4e5f60 + id * 0x9e3779).toString(16)}`
}

export function messageHash(id: number) {
  return `${(0xa3f9c1 + id * 0x3d70a3).toString(16).slice(-6)}…`
}

export const initialDemoState: DemoState = {
  phase: 'idle',
  step: 0,
  rows: Array.from({ length: VISIBLE_ROWS - 1 }, (_, index) => ({
    id: -1 - index,
    purchase: purchaseAt(PURCHASES.length - 1 - index),
  })),
  balance: 248.6,
  starsSpend: 312.4,
  premiumSpend: 128.2,
  chart: CHART_SEED,
}

function addToChart(chart: ChartPoint[], purchase: DemoPurchase) {
  const last = chart[chart.length - 1]

  // A full last bucket rolls the chart over to a new day.
  if (last[purchase.kind] + purchase.amount > CHART_MAX * 0.9) {
    const day = { stars: 0, premium: 0, [purchase.kind]: purchase.amount }
    return [...chart.slice(1), day]
  }

  return [
    ...chart.slice(0, -1),
    { ...last, [purchase.kind]: last[purchase.kind] + purchase.amount },
  ]
}

export function demoReducer(state: DemoState, action: DemoAction): DemoState {
  switch (action.type) {
    case 'send':
      return state.phase === 'idle' ? { ...state, phase: 'sending' } : state

    case 'complete': {
      if (state.phase !== 'sending') return state

      const purchase = purchaseAt(state.step)
      const balance = state.balance - purchase.amount
      const spendKey = purchase.kind === 'stars' ? 'starsSpend' : 'premiumSpend'

      return {
        ...state,
        phase: 'done',
        rows: [{ id: state.step, purchase }, ...state.rows].slice(
          0,
          VISIBLE_ROWS,
        ),
        // Reads as a deposit landing, and keeps the loop from going negative.
        balance: balance < LOW_BALANCE ? balance + TOP_UP : balance,
        [spendKey]: state[spendKey] + purchase.amount,
        chart: addToChart(state.chart, purchase),
      }
    }

    case 'next':
      return state.phase === 'done'
        ? { ...state, phase: 'idle', step: state.step + 1 }
        : state
  }
}

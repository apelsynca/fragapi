import type { TonTransaction } from './ton-transaction'

export interface Deposit {
  amount: number
  createdAt: string
  status: 'pending' | 'failed' | 'completed'
  tonTransaction: TonTransaction | null
}

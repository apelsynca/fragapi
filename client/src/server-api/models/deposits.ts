import type { TonTransaction } from './ton-transaction'

export interface Deposit {
  amount: number
  createdAt: string
  status: 'pending' | 'completed'
  tonTransaction: TonTransaction | null
}

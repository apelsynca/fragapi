import type { TonTransaction } from './ton-transaction'

type FragmentTransactionReason = 'stars' | 'premium'

export interface FragmentTransaction {
  amount: number
  reason: FragmentTransactionReason
  recipient: string
  recipientUsername: string

  starsAmount: number | null
  premiumMonths: number | null

  tonTransaction: TonTransaction

  createdAt: string
}

export interface TransactionsStats {
  totalSpend: number
  starsTotalSpend: number
  premiumTotalSpend: number
}

export interface TransactionChartPoint {
  date: string
  starsSpend: number
  premiumSpend: number
}

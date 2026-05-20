type FragmentTransactionReason = 'stars' | 'premium'

export interface FragmentTransaction {
  amount: number
  reason: FragmentTransactionReason
  recipient: string
  recipientUsername: string

  starsAmount: number | null
  premiumMonths: number | null

  createdAt: string
}

export interface TransactionsStats {
  totalSpend: number
  starsTotalSpend: number
  premiumTotalSpend: number
}

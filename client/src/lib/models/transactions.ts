export interface Transaction {
  amount: number
  reason: 'premium' | 'stars'
  status: 'pending' | 'completed' | 'failed'
  message_hash: string | null
  recipient: string
  created_at: string
}

export interface TransactionStats {
  starsPurchasesCount: number
  premiumCount: number
  totalSpent: number
}

export interface TransChartPoint {
  date: string
  tonAmount: number
  transactionsCount: number
}

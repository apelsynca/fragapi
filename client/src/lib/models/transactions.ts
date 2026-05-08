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

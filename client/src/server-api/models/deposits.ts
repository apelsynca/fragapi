interface Transaction {
  hash: string | null
}

export interface Deposit {
  amount: number
  createdAt: string
  status: 'pending' | 'completed'
  transaction: Transaction | null
}

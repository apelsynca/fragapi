interface Transaction {
  hash: string | null
}

export interface Payment {
  amount: number
  createdAt: string
  status: 'pending' | 'completed'
  transaction: Transaction | null
}

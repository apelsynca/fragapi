export interface Payment {
  amount: number
  createdAt: string
  status: 'pending' | 'completed'
}

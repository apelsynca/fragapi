export enum TransactionReason {
  PREMIUM = "premium",
  STARS = "stars",
}

export interface Transaction {
  amount: number;
  reason: TransactionReason;
  created_at: Date;
}

export interface TransactionStats {
  stars_count: number;
  premium_count: number;
  total_spent: number;
}

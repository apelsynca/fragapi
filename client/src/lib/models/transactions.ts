export enum TransactionReason {
  PREMIUM = "premium",
  STARS = "stars",
}

export interface Transaction {
  amount: number;
  reason: TransactionReason;
  created_at: Date;
}

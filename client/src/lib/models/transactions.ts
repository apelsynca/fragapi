export enum TransactionReason {
  PREMIUM = "premium",
  STARS = "stars",
}

export enum TransactionStatus {
  PENDING = "pending",
  COMPLETED = "completed",
  FAILED = "failed",
}

export interface Transaction {
  id: number;
  amount: number;
  reason: TransactionReason;
  status: TransactionStatus;
  tx_hash: string | null;
  starsQuantity: number | null;
  recipient: string | null;
  created_at: Date;
}

export interface TransactionStats {
  starsPurchasesCount: number;
  premiumCount: number;
  totalSpent: number;
}

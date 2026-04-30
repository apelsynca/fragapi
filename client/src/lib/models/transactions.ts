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
  txHash: string | null;
  starsQuantity: number | null;
  recipient: string | null;
  createdAt: Date;
}

export interface TransactionStats {
  starsPurchasesCount: number;
  premiumCount: number;
  totalSpent: number;
}

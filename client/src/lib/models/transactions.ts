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
  stars_quantity: number | null;
  recipient: string | null;
  created_at: Date;
}

export interface TransactionStats {
  stars_purchases_count: number;
  premium_count: number;
  total_spent: number;
}

export interface TransactionVerifyResponse {
  id: number;
  status: TransactionStatus;
  tx_hash: string | null;
  verified: boolean;
  message: string;
}

export interface Pagination {
  total_count: number;
  max_page: number;
}

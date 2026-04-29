export interface User {
  id: number;
  firstName: string;
  lastName: string;
  username: string;
  balance: number;
  apiKey: string;
}

export interface TokenRevoked {
  success: boolean;
  apiKey: string;
}

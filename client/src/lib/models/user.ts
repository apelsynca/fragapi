export interface User {
  id: number;
  first_name: string;
  last_name: string;
  username: string;
  balance: number;
  api_key: string;
}

export interface TokenRevoked {
  success: boolean;
  api_key: string;
}

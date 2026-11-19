export interface User {
  id: number
  firstName: string
  lastName: string | null
  username: string | null
  balance: number
}

export interface RevokeTokenResponse {
  success: boolean
  apiKey: string
}

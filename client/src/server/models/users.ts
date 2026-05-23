export interface User {
  firstName: string
  lastName: string | null
  username: string | null
  id: number
  balance: number
  apiKey: string
}

export interface RevokeTokenResponse {
  success: boolean
  apiKey: string
}

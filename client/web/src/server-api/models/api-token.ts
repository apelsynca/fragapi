export interface ApiToken {
  id: string
  name: string
  token: string
  expiresAt: string | null // NOTE: can be Date
  lastUsedAt: string | null // NOTE: can be Date
}

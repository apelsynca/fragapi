export interface ApiToken {
  id: string
  name: string
  token: string
  expires_at: string | null // NOTE: can be Date
  last_used_at: string | null // NOTE: can be Date
}

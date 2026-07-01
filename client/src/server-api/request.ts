import { logoutFn } from './auth-manager'

const ENDPOINT = process.env.BACKEND_ENDPOINT

interface ApiRequest {
  method: 'GET' | 'POST' | 'DELETE'
  endpoint: string
  payload?: object | null
  token?: string
}

export const apiRequest = async <T>(data: ApiRequest) => {
  const defaultHeaders = { 'Content-Type': 'application/json' }

  const response = await fetch(`${ENDPOINT}${data.endpoint}`, {
    method: data.method,
    headers: data.token
      ? { Authorization: `Bearer ${data.token}`, ...defaultHeaders }
      : defaultHeaders,
    body: JSON.stringify(data.payload),
  })

  const json = await response.json()

  if (!response.ok) {
    const errorName = json?.error ?? 'Non-standard error'
    const detail = json?.detail ?? ''

    if (data.token && errorName === 'Unauthorized') {
      await logoutFn()
    }

    throw new Error(`${errorName} ${JSON.stringify(detail)}`)
  }

  return json as T
}

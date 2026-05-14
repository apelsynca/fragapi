import { logoutFn } from './auth-manager'

const ENDPOINT = process.env.BACKEND_ENDPOINT

interface ApiRequest {
  method: 'GET' | 'POST'
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
    console.log(response.status, json)
    const errorName = json?.error ?? 'Some unknown error'
    const detail = json?.detail ?? ''

    if (data.token && errorName === 'Unauthorized') {
      console.log(data.token)
      await logoutFn()
    }

    throw new Error(`${errorName} ${detail}`)
  }

  return json as T
}

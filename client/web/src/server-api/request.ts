import { logoutFn } from './auth-manager'

const ENDPOINT = process.env.BACKEND_ENDPOINT

const REQUEST_TIMEOUT_MS = 15_000

export class ApiError extends Error {
  status: number
  errorName: string
  detail: unknown

  constructor(status: number, errorName: string, detail: unknown) {
    super(formatMessage(errorName, detail))
    this.name = 'ApiError'
    this.status = status
    this.errorName = errorName
    this.detail = detail
  }
}

function formatMessage(errorName: string, detail: unknown) {
  if (detail == null) return errorName

  const detailText =
    typeof detail === 'string' ? detail : JSON.stringify(detail)

  return `${errorName}: ${detailText}`
}

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
    ...(data.payload != null ? { body: JSON.stringify(data.payload) } : {}),
    signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
  })

  const json = await response.json().catch(() => null)

  if (!response.ok) {
    if (response.status === 401 && data.token) {
      await logoutFn()
    }

    throw new ApiError(
      response.status,
      json?.error ?? `HTTP ${response.status}`,
      json?.detail ?? null,
    )
  }

  return json as T
}

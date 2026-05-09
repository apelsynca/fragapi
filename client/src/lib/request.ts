import { createServerFn } from '@tanstack/react-start'
import { verifySession } from './auth'

const ENDPOINT = process.env.NITRO_BACKEND_ENDPOINT

interface RequestData {
  method: 'GET' | 'POST'
  endpoint: string
  json?: object | null
  token?: string
}

export const doRequest = async (data: RequestData): Promise<Response> => {
  const defaultHeaders = { 'Content-Type': 'application/json' }

  return await fetch(`${ENDPOINT}${data.endpoint}`, {
    method: data.method,
    headers: data.token
      ? { Authorization: `Bearer ${data.token}`, ...defaultHeaders }
      : defaultHeaders,
    body: JSON.stringify(data.json),
  })
}

interface ApiRequest {
  method: 'GET' | 'POST'
  endpoint: string
  payload?: object | null
}

export const apiRequest = createServerFn()
  .inputValidator((data: ApiRequest) => data)
  .handler(async ({ data: { method, endpoint, payload } }) => {
    const token = await verifySession()

    const response = await doRequest({
      method,
      endpoint,
      token,
      json: payload,
    })

    if (!response.ok) {
      throw new Error('CHANGE THIS MAYBE?')
    }

    return await response.json()
  })

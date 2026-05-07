const ENDPOINT = process.env.BACKEND_ENDPOINT

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

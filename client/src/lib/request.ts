const ENDPOINT = process.env.BACKEND_ENDPOINT

interface ApiRequest {
  method: 'GET' | 'POST'
  endpoint: string
  payload?: object | null
  token?: string
}

export const apiRequest = async (data: ApiRequest) => {
  const defaultHeaders = { 'Content-Type': 'application/json' }

  const response = await fetch(`${ENDPOINT}${data.endpoint}`, {
    method: data.method,
    headers: data.token
      ? { Authorization: `Bearer ${data.token}`, ...defaultHeaders }
      : defaultHeaders,
    body: JSON.stringify(data.payload),
  })

  if (!response.ok) {
    console.log('this is an error')
    throw new Error('Some error, idk what')
  }

  return await response.json()
}

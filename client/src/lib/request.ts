import { createServerFn } from '@tanstack/react-start'
import { verifySession } from './auth'

const ENDPOINT = process.env.BACKEND_ENDPOINT

interface RequestData {
  method: 'GET' | 'POST'
  endpoint: string
  json?: object | null
  token?: string
}

export const doRequest = async (data: RequestData): Promise<Response> => {
  const defaultHeaders = { 'Content-Type': 'application/json' }
  // #region agent log
  fetch('http://127.0.0.1:7329/ingest/95404717-411f-4aed-8ae1-e31a43e53fe5',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'37dd5b'},body:JSON.stringify({sessionId:'37dd5b',runId:'initial',hypothesisId:'H1-H4',location:'src/lib/request.ts:17',message:'doRequest:start',data:{method:data.method,endpoint:data.endpoint,hasToken:Boolean(data.token),hasBackendEndpoint:Boolean(ENDPOINT)},timestamp:Date.now()})}).catch(()=>{});
  // #endregion

  const response = await fetch(`${ENDPOINT}${data.endpoint}`, {
    method: data.method,
    headers: data.token
      ? { Authorization: `Bearer ${data.token}`, ...defaultHeaders }
      : defaultHeaders,
    body: JSON.stringify(data.json),
  })

  // #region agent log
  fetch('http://127.0.0.1:7329/ingest/95404717-411f-4aed-8ae1-e31a43e53fe5',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'37dd5b'},body:JSON.stringify({sessionId:'37dd5b',runId:'initial',hypothesisId:'H2-H5',location:'src/lib/request.ts:29',message:'doRequest:response',data:{endpoint:data.endpoint,status:response.status,ok:response.ok,url:response.url},timestamp:Date.now()})}).catch(()=>{});
  // #endregion

  return response
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
      // #region agent log
      fetch('http://127.0.0.1:7329/ingest/95404717-411f-4aed-8ae1-e31a43e53fe5',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'37dd5b'},body:JSON.stringify({sessionId:'37dd5b',runId:'initial',hypothesisId:'H2-H5',location:'src/lib/request.ts:50',message:'apiRequest:not_ok',data:{endpoint,status:response.status,ok:response.ok},timestamp:Date.now()})}).catch(()=>{});
      // #endregion
      throw new Error('CHANGE THIS MAYBE?')
    }

    return await response.json()
  })

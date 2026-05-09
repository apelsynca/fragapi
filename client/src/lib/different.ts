import { createServerFn } from '@tanstack/react-start'
import type { TransactionStats, TransChartPoint } from './models/transactions'
import { apiRequest } from './request'

export const fetchATransactionStats = createServerFn().handler(async () => {
  // #region agent log
  fetch('http://127.0.0.1:7329/ingest/95404717-411f-4aed-8ae1-e31a43e53fe5',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'37dd5b'},body:JSON.stringify({sessionId:'37dd5b',runId:'initial',hypothesisId:'H1-H3',location:'src/lib/different.ts:7',message:'fetchATransactionStats:start',data:{endpoint:'/transactions/stats'},timestamp:Date.now()})}).catch(()=>{});
  // #endregion
  return (await apiRequest({
    data: {
      method: 'GET',
      endpoint: '/transactions/stats',
    },
  })) as TransactionStats
})

export const fetchATransactionsChart = createServerFn().handler(async () => {
  // #region agent log
  fetch('http://127.0.0.1:7329/ingest/95404717-411f-4aed-8ae1-e31a43e53fe5',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'37dd5b'},body:JSON.stringify({sessionId:'37dd5b',runId:'initial',hypothesisId:'H1-H3',location:'src/lib/different.ts:18',message:'fetchATransactionsChart:start',data:{endpoint:'/transactions/chart'},timestamp:Date.now()})}).catch(()=>{});
  // #endregion
  return (await apiRequest({
    data: {
      method: 'GET',
      endpoint: '/transactions/chart',
    },
  })) as TransChartPoint[]
})

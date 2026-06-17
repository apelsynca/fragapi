import { useSuspenseQuery } from '@tanstack/react-query'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '../ui/card'
import { paymentHistoryOptions } from '#/lib/queries'
import { useState } from 'react'
import BreadPagination from '#/layout/BreadPagination'

export default function PaymentHistory() {
  const [currentPage, setCurrentPage] = useState<number>(1)
  const { data } = useSuspenseQuery(paymentHistoryOptions(currentPage))

  if (data.pagination.totalCount < 0) {
    return <p>No transactions.</p>
  }

  const maxPage = data.pagination.maxPage

  return (
    <Card>
      <CardHeader>
        <CardTitle>История пополнений</CardTitle>
        <CardDescription>История пополнений вашего баланса</CardDescription>
      </CardHeader>
      <CardContent>
        {maxPage > 1 && (
          <BreadPagination
            page={currentPage}
            maxPage={data.pagination.maxPage}
            setPage={setCurrentPage}
          />
        )}
      </CardContent>
      <CardFooter></CardFooter>
    </Card>
  )
}

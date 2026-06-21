import { useSuspenseQuery } from '@tanstack/react-query'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '../ui/card'
import { depositsOptions } from '#/lib/queries'
import { useState } from 'react'
import BreadPagination from '#/layout/BreadPagination'
import { DataTable } from '../DataTable'
import { columns } from './columns'
import { m } from '#/paraglide/messages'

export default function DepositHistory() {
  const [currentPage, setCurrentPage] = useState<number>(1)
  const { data } = useSuspenseQuery(depositsOptions(currentPage))

  if (data.pagination.totalCount < 0) {
    return <p>No transactions.</p>
  }

  const maxPage = data.pagination.maxPage

  return (
    <Card>
      <CardHeader className="flex items-center gap-2 md:gap-5">
        <div>
          <CardTitle>{m.deposits_history_title()}</CardTitle>
          <CardDescription>{m.deposits_history_description()}</CardDescription>
        </div>
      </CardHeader>
      <CardContent>
        <DataTable columns={columns} data={data.items} />
      </CardContent>
      <CardFooter>
        {maxPage > 1 && (
          <BreadPagination
            page={currentPage}
            maxPage={maxPage}
            setPage={setCurrentPage}
          />
        )}
      </CardFooter>
    </Card>
  )
}

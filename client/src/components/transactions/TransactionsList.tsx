import { useSuspenseQuery } from '@tanstack/react-query'
import { columns } from './columns'
import { DataTable } from '../DataTable'
import { transactionsListOptions } from '#/lib/queries'
import { useState } from 'react'
import BreadPagination from '#/layout/BreadPagination'

export default function TransactionsList() {
  const [currentPage, setCurrentPage] = useState<number>(1)
  const { data } = useSuspenseQuery(transactionsListOptions(currentPage))

  if (data.pagination.totalCount < 0) {
    return <p>No transactions.</p>
  }

  const maxPage = data.pagination.maxPage

  return (
    <div className="flex flex-col gap-4">
      <DataTable columns={columns} data={data.items} />

      {maxPage > 1 && (
        <BreadPagination
          page={currentPage}
          maxPage={data.pagination.maxPage}
          setPage={setCurrentPage}
        />
      )}
    </div>
  )
}

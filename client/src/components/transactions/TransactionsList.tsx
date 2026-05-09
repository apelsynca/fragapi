import { useSuspenseQuery } from '@tanstack/react-query'
import { columns } from './columns'
import { DataTable } from './DataTable'
import { transactionsListQueryOptions } from '~/lib/queries'
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '~/components/ui/pagination'
import { useState } from 'react'

export default function TransactionsList() {
  const [currentPage, setCurrentPage] = useState<number>(1)

  const { data } = useSuspenseQuery(transactionsListQueryOptions(currentPage))

  return (
    <div className="flex flex-col gap-4">
      <DataTable columns={columns} data={data.items} />

      <Pagination>
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious
              href="#"
              onClick={() =>
                setCurrentPage((prev) => (prev < 2 ? 1 : prev - 1))
              }
            />
          </PaginationItem>
          <PaginationItem>
            <PaginationEllipsis />
          </PaginationItem>
          <PaginationItem>
            <PaginationNext
              href="#"
              onClick={() =>
                setCurrentPage((prev) =>
                  prev >= data.pagination.maxPage ? prev : prev + 1,
                )
              }
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  )
}

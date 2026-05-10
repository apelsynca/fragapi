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
            <PaginationLink
              href="#"
              onClick={() => setCurrentPage(1)}
              isActive={currentPage === 1}
            >
              1
            </PaginationLink>
          </PaginationItem>
          {data.pagination.maxPage > 2 && (
            <PaginationItem>
              <PaginationEllipsis />
            </PaginationItem>
          )}
          {data.pagination.maxPage > 1 && (
            <PaginationItem>
              <PaginationLink
                href="#"
                onClick={() => setCurrentPage(data.pagination.maxPage)}
                isActive={currentPage === data.pagination.maxPage}
              >
                {data.pagination.maxPage}
              </PaginationLink>
            </PaginationItem>
          )}
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

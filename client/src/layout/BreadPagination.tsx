import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
  PaginationEllipsis,
} from '#/components/ui/pagination'
import { getPageNumbers } from '#/utils/bread-pagination'

export default function BreadPagination({
  page: currentPage,
  maxPage,
  setPage,
}: {
  page: number
  maxPage: number
  setPage: React.Dispatch<React.SetStateAction<number>>
}) {
  return (
    <Pagination>
      <PaginationContent>
        <PaginationItem>
          <PaginationPrevious
            onClick={() => setPage((prev) => Math.max(1, prev - 1))}
          />
        </PaginationItem>

        {getPageNumbers(currentPage, maxPage).map((page, idx) =>
          page === 'ellipsis' ? (
            <PaginationItem key={`ellipsis-${idx}`}>
              <PaginationEllipsis />
            </PaginationItem>
          ) : (
            <PaginationItem key={page}>
              <PaginationLink
                onClick={() => setPage(page)}
                isActive={currentPage === page}
              >
                {page}
              </PaginationLink>
            </PaginationItem>
          ),
        )}

        <PaginationItem>
          <PaginationNext
            onClick={() => setPage((prev) => Math.min(maxPage, prev + 1))}
          />
        </PaginationItem>
      </PaginationContent>
    </Pagination>
  )
}

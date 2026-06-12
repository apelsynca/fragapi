interface Pagination {
  totalCount: number
  maxPage: number
}

export interface ListResource<T> {
  items: T[]
  pagination: Pagination
}

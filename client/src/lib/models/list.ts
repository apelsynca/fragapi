export interface Pagination {
  total_count: number;
  max_page: number;
}

export interface ListResource<T> {
  items: T[];
  pagination: Pagination;
}
